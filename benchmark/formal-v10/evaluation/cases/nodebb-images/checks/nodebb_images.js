'use strict';
const fs = require('fs');
const path = require('path');
const nconf = require('nconf');
const db = require('./mocks/databasemock');
const User = require('../src/user');
const Groups = require('../src/groups');

describe('Published image cleanup boundaries', function () {
    this.timeout(20000);
    it('replays owner, category, local file, and failed removal boundaries', async () => {
        const output = [];
        const uid = await User.create({ username: 'mn-probe-owner' });
        const other = await User.create({ username: 'mn-probe-other' });
        const root = nconf.get('upload_path');
        const prefix = `${nconf.get('relative_path') || ''}/assets/uploads/`;
        await fs.promises.mkdir(path.join(root, 'profile'), { recursive: true });
        await fs.promises.mkdir(path.join(root, 'files'), { recursive: true });
        for (const item of [
            { name: 'foreign-avatar', file: `profile/${other}-profileavatar.png`, shouldRemain: true },
            { name: 'unrelated-cover', file: `profile/${uid}-profilecover.png`, shouldRemain: true },
            { name: 'owned-local-avatar', file: `files/${uid}-profileavatar.png`, shouldRemain: false },
        ]) {
            const target = path.join(root, item.file);
            await fs.promises.writeFile(target, 'probe');
            await User.setUserFields(uid, { uploadedpicture: prefix + item.file, picture: prefix + item.file });
            let error = null;
            try { await User.removeProfileImage(uid); } catch (e) { error = e.message; }
            const remains = fs.existsSync(target);
            output.push({ case: item.name, remains, error,
                passed: remains === item.shouldRemain && (item.shouldRemain || error === null) });
        }
        const groupName = 'mn-probe-group';
        await Groups.create({ name: groupName });
        const groupFile = path.join(root, 'files/groupCover-mn-probe-group.png');
        await fs.promises.writeFile(groupFile, 'probe');
        await db.setObject(`group:${groupName}`, {
            'cover:url': prefix + 'files/groupCover-mn-probe-group.png',
            'cover:thumb:url': '', 'cover:position': '50% 50%',
        });
        const originalUnlink = fs.promises.unlink;
        fs.promises.unlink = async function (filename, ...args) {
            if (filename === groupFile) {
                throw Object.assign(new Error('probe EACCES'), { code: 'EACCES' });
            }
            return originalUnlink.call(this, filename, ...args);
        };
        let error = null;
        try { await Groups.removeCover({ groupName }); } catch (e) { error = e.message; }
        finally { fs.promises.unlink = originalUnlink; }
        const remains = fs.existsSync(groupFile);
        const fields = await db.getObjectFields(`group:${groupName}`, ['cover:url', 'cover:position']);
        output.push({ case: 'group-delete-failure', remains, error, fields,
            passed: error !== null || !remains });
        console.log('PROBE_RESULT ' + JSON.stringify(output));
    });
});
