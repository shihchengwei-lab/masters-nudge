import { parseToVCard, vCardPropertiesToICAL } from '@proton/shared/lib/contacts/vcard';
import { getVCardProperties } from '@proton/shared/lib/contacts/properties';
import { prepareForSaving } from '@proton/shared/lib/contacts/surgery';

it('keeps parsed false preferences in the contact save serialization path', () => {
    const input = [
        'BEGIN:VCARD', 'VERSION:4.0', 'FN:Contact',
        'ITEM1.EMAIL:a@example.com', 'ITEM1.X-PM-ENCRYPT:true',
        'ITEM2.EMAIL:b@example.com', 'ITEM2.X-PM-ENCRYPT-UNTRUSTED:false',
        'ITEM3.EMAIL:c@example.com', 'ITEM3.X-PM-ENCRYPT:false', 'END:VCARD',
    ].join('\r\n');
    const parsed = parseToVCard(input);
    const serialized = vCardPropertiesToICAL(getVCardProperties(prepareForSaving(parsed))).toString();
    const result = {
        parsedUntrusted: parsed['x-pm-encrypt-untrusted']?.[0]?.value,
        parsedPinned: parsed['x-pm-encrypt']?.find((p) => p.group === 'item3')?.value,
        preservedUntrusted: /(?:^|\r?\n)ITEM2\.X-PM-ENCRYPT-UNTRUSTED:false(?:\r?\n|$)/.test(serialized),
        preservedPinned: /(?:^|\r?\n)ITEM3\.X-PM-ENCRYPT:false(?:\r?\n|$)/.test(serialized),
        preservedTrueControl: /(?:^|\r?\n)ITEM1\.X-PM-ENCRYPT:true(?:\r?\n|$)/.test(serialized),
        serialized,
    };
    console.log('PROBE_RESULT ' + JSON.stringify({ ...result,
        passed: result.preservedUntrusted && result.preservedPinned && result.preservedTrueControl }));
});
