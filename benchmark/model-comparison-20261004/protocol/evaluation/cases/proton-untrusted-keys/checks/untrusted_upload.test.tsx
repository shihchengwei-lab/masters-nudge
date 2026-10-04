import { act, fireEvent, waitFor } from '@testing-library/react';
import { CryptoProxy } from '@proton/crypto';
import { API_CODES, CONTACT_CARD_TYPE } from '@proton/shared/lib/constants';
import { parseToVCard } from '@proton/shared/lib/contacts/vcard';
import { VCardProperty } from '@proton/shared/lib/interfaces/contacts/VCard';
import { api, clearAll, mockedCryptoApi, notificationManager, render } from '../tests/render';
import ContactEmailSettingsModal from './ContactEmailSettingsModal';

// Replace only file selection. The actual upload handler, state updates, modal,
// model effect, key serialization and save callback all run unchanged.
jest.mock('../../keys/shared/SelectKeyFiles', () => ({
    __esModule: true,
    default: ({ onUpload }: any) => (
        <button onClick={() => void onUpload([{ keyIsPrivate: false, armoredKey: 'uploaded-public-key' }])}>
            Upload probe key
        </button>
    ),
}));

beforeEach(clearAll);
afterEach(async () => CryptoProxy.releaseEndpoint());

it('records the default pinned encryption preference after the first key is uploaded', async () => {
    CryptoProxy.setEndpoint({
        ...mockedCryptoApi,
        importPublicKey: jest.fn().mockResolvedValue({
            getFingerprint: () => 'abcdef',
            getCreationTime: () => new Date(0),
            getExpirationTime: () => Infinity,
            getAlgorithmInfo: () => ({ algorithm: 'eddsa', curve: 'curve25519' }),
            subkeys: [],
            getUserIDs: () => ['<user@example.com>'],
        }),
        canKeyEncrypt: jest.fn().mockResolvedValue(true),
        exportPublicKey: jest.fn().mockResolvedValue(new Uint8Array([1, 2, 3])),
        isExpiredKey: jest.fn().mockResolvedValue(false),
        isRevokedKey: jest.fn().mockResolvedValue(false),
    });
    const card = parseToVCard([
        'BEGIN:VCARD', 'VERSION:4.0', 'FN:User', 'ITEM1.EMAIL:user@example.com', 'END:VCARD',
    ].join('\r\n'));
    const save = jest.fn();
    api.mockImplementation(async (args: any): Promise<any> => {
        if (args.url === 'keys') return { Keys: [] };
        if (args.url === 'contacts/v4/contacts') {
            save(args.data);
            return { Responses: [{ Response: { Code: API_CODES.SINGLE_SUCCESS } }] };
        }
    });
    const { getByText } = render(
        <ContactEmailSettingsModal open contactID="ContactID" vCardContact={card}
            emailProperty={card.email?.[0] as VCardProperty<string>} />
    );
    const advanced = getByText('Show advanced PGP settings');
    await waitFor(() => expect(advanced).not.toBeDisabled());
    fireEvent.click(advanced);
    expect(document.getElementById('encrypt-toggle')).toBeDisabled();
    fireEvent.click(getByText('Upload probe key'));
    await waitFor(() => expect(document.getElementById('encrypt-toggle')).toBeEnabled());
    await act(async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); });
    const encryptChecked = (document.getElementById('encrypt-toggle') as HTMLInputElement).checked;
    fireEvent.click(getByText('Save'));
    await waitFor(() => expect(save).toHaveBeenCalled());
    const signed = save.mock.calls[0][0].Contacts[0].Cards.find(
        ({ Type }: { Type: CONTACT_CARD_TYPE }) => Type === CONTACT_CARD_TYPE.SIGNED
    ).Data as string;
    const hasKey = /(?:^|\r?\n)ITEM1\.KEY[:;]/.test(signed);
    const hasPinnedPreference = signed.includes('ITEM1.X-PM-ENCRYPT:true');
    const hasSignPreference = signed.includes('ITEM1.X-PM-SIGN:true');
    const result = { hasKey, encryptChecked, hasPinnedPreference, hasSignPreference, signed,
        passed: hasKey && encryptChecked && hasPinnedPreference && hasSignPreference };
    console.log('PROBE_RESULT ' + JSON.stringify(result));
});
