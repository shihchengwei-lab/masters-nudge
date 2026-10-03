'use strict';
const fs = require('fs');
const path = require('path');
const nconf = require('nconf');
const db = require('./mocks/databasemock');
const Groups = require('../src/groups');
const File = require('../src/file');

describe('Published group cover zero-files requirement', function () {
    this.timeout(20000);
    it('removes retained formats created by group-specific upload naming', async () => {
        const groupName = 'mn-variants-owner';
        await Groups.create({ name: groupName });
        const directory = path.join(nconf.get('upload_path'), 'files');
        await fs.promises.mkdir(directory, { recursive: true });
        // updateCover writes extension-specific names and overwrites the URL fields.
        const names = ['groupCover', 'groupCoverThumb'].flatMap(kind =>
            ['png', 'jpeg'].map(ext => `${kind}-${groupName}.${ext}`));
        const temp = path.join(nconf.get('upload_path'), 'mn-group-variant-fixture');
        await fs.promises.writeFile(temp, 'image-fixture');
        const uploads = [];
        for (const filename of [...names, 'groupCover-mn-variants-other.png']) {
            uploads.push(await File.saveFileToLocal(filename, 'files', temp));
        }
        await fs.promises.unlink(temp);
        const related = uploads.slice(0, 4).map(upload => upload.path);
        const unrelated = uploads[4].path;
        await db.setObject(`group:${groupName}`, {
            'cover:url': uploads[1].url,
            'cover:thumb:url': uploads[3].url,
            'cover:position': '50% 50%',
        });
        let error = null;
        try { await Groups.removeCover({ groupName }); } catch (e) { error = e.message; }
        const remaining = related.filter(filename => fs.existsSync(filename)).map(filename => path.basename(filename));
        const unrelatedRemains = fs.existsSync(unrelated);
        const fields = await db.getObjectFields(`group:${groupName}`, ['cover:url', 'cover:thumb:url', 'cover:position']);
        console.log('PROBE_RESULT ' + JSON.stringify([{
            case: 'retained-group-formats', remaining, unrelatedRemains, fields, error,
            passed: error === null && remaining.length === 0 && unrelatedRemains && Object.values(fields).every(value => value === null),
        }]));
    });
});
