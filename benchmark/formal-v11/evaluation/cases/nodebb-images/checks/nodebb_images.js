'use strict';
const fs = require('fs');
const path = require('path');
const nconf = require('nconf');
const db = require('./mocks/databasemock');
const User = require('../src/user');
const Groups = require('../src/groups');
const File = require('../src/file');

describe('Published image cleanup boundaries', function () {
    this.timeout(20000);
    it('replays owner, category, local file, and failed removal boundaries', async () => {
        const output = [];
        const uid = await User.create({ username: 'mn-probe-owner' });
        const other = await User.create({ username: 'mn-probe-other' });
        const root = nconf.get('upload_path');
        const fixture = path.join(root, 'mn-image-cleanup-fixture');
        await fs.promises.mkdir(root, { recursive: true });
        await fs.promises.writeFile(fixture, 'probe');
        for (const item of [
            { name: 'foreign-avatar', file: `profile/${other}-profileavatar.png`, shouldRemain: true },
            { name: 'unrelated-cover', file: `profile/${uid}-profilecover.png`, shouldRemain: true },
            { name: 'owned-local-avatar', file: `files/${uid}-profileavatar.png`, shouldRemain: false },
        ]) {
            // Store the upload API's raw URL; getters add the deployment prefix.
            const upload = await File.saveFileToLocal(path.basename(item.file), path.dirname(item.file), fixture);
            const target = upload.path;
            await User.setUserFields(uid, { uploadedpicture: upload.url, picture: upload.url });
            let error = null;
            try { await User.removeProfileImage(uid); } catch (e) { error = e.message; }
            const remains = fs.existsSync(target);
            output.push({ case: item.name, remains, error, uploadedUrl: upload.url,
                passed: remains === item.shouldRemain && (item.shouldRemain || error === null) });
        }
        const groupName = 'mn-probe-group';
        await Groups.create({ name: groupName });
        const groupUpload = await File.saveFileToLocal(`groupCover-${groupName}.png`, 'files', fixture);
        const groupFile = groupUpload.path;
        await fs.promises.unlink(fixture);
        await db.setObject(`group:${groupName}`, {
            'cover:url': groupUpload.url,
            'cover:thumb:url': '', 'cover:position': '50% 50%',
        });
        const originalUnlink = fs.promises.unlink;
        let unlinkCalls = 0;
        fs.promises.unlink = async function (filename, ...args) {
            if (filename === groupFile) {
                unlinkCalls += 1;
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
            uploadedUrl: groupUpload.url, unlinkCalls,
            passed: error !== null || !remains });
        console.log('PROBE_RESULT ' + JSON.stringify(output));
    });
});
