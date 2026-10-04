import { act } from '@testing-library/react';
import { wait } from '@proton/shared/lib/helpers/promise';
import { clearAll, addApiMock } from '../../../helpers/test/helper';
import { store } from '../../../logic/store';
import * as actions from '../../../logic/elements/elementsActions';
import * as reducers from '../../../logic/elements/elementsReducers';
import { pendingActions } from '../../../logic/elements/elementsSelectors';
import { getElements, setup, expectElements } from './Mailbox.test.helpers';

jest.setTimeout(20000);

describe('Published mailbox contract', () => {
    beforeEach(clearAll);

    it('exposes the documented actions, reducers and operation-count selector', () => {
        for (const name of ['retryStale', 'backendActionStarted', 'backendActionFinished'] as const) {
            expect(typeof actions[name]).toBe('function');
            expect(typeof reducers[name]).toBe('function');
        }
        const queryParameters = { Page: 0 };
        const stale = actions.retryStale({ queryParameters });
        expect(typeof stale.type).toBe('string');
        expect(stale.payload).toEqual({ queryParameters });
        const before = pendingActions(store.getState());
        store.dispatch(actions.backendActionStarted());
        expect(pendingActions(store.getState())).toBe(before + 1);
        store.dispatch(actions.backendActionFinished());
        expect(pendingActions(store.getState())).toBe(before);
        console.log('PROBE_RESULT ' + JSON.stringify({ check: 'public-interfaces', passed: true }));
    });

    it.each([
        ['failure', 2000],
        ['stale', 1000],
    ] as const)('holds the %s retry until all modifying operations settle', async (kind, delay) => {
        const conversations = getElements(3);
        let settleResponse!: (value: any) => void;
        let attempts = 0;
        const request = jest.fn(() => {
            attempts++;
            if (attempts === 1) {
                if (kind === 'failure') throw new Error('Contract test request failure');
                return { Total: conversations.length, Conversations: conversations, Stale: 1 };
            }
            return new Promise((resolve) => { settleResponse = resolve; });
        });
        addApiMock('mail/v4/conversations', request, 'get');
        const { getItems } = await setup({ mockConversations: false, totalConversations: conversations.length });
        const expectLoading = () => {
            const count = getItems().length;
            expect(count).toBeGreaterThan(0);
            expectElements(getItems, count, true);
        };
        expect(request).toHaveBeenCalledTimes(1);
        expectLoading();

        await act(async () => {
            store.dispatch(actions.backendActionStarted());
            store.dispatch(actions.backendActionStarted());
        });
        await act(async () => { await wait(delay); });
        expect(request).toHaveBeenCalledTimes(1);
        expectLoading();

        await act(async () => { store.dispatch(actions.backendActionFinished()); });
        expect(request).toHaveBeenCalledTimes(1);
        expectLoading();

        // act flushes the ordinary React update/effect cycle. A request need not
        // be issued inside the reducer or the backendActionFinished dispatch.
        await act(async () => { store.dispatch(actions.backendActionFinished()); });
        expect(request).toHaveBeenCalledTimes(2);
        expectLoading();

        await act(async () => {
            settleResponse({ Total: conversations.length, Conversations: conversations, Stale: 0 });
        });
        expect(request).toHaveBeenCalledTimes(2);
        expectElements(getItems, conversations.length, false);
        console.log('PROBE_RESULT ' + JSON.stringify({ check: kind + '-operation-overlap', passed: true }));
    });
});
