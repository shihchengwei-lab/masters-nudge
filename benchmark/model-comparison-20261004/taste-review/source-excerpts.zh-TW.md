# 覆核程式摘錄

以下逐字摘自覆核使用的完整程式版本；行號對應 sources.zip 內的同名檔案。完整版本及指紋見 [程式來源包](sources.zip)與[來源索引](sources-index.json)。

這些程式來自各題上游專案，沿用該專案授權；授權文件保存在[各題材料](../protocol/evaluation/cases)的 `upstream-licenses/` 目錄。

<a id="source-1"></a>

## I2：完整模型重建與取消保護

完整檔案：`sources/proton-untrusted-keys/I2/packages/components/containers/contacts/email/ContactEmailSettingsModal.tsx`；摘錄行號：219–278。

SHA-256：`5ee32cbe976f26bbc9d41ffd3905524d14a17ac0a3c4b7bafb3a34c7c0bb207d`。

```text
 219           * When the list of trusted, expired or revoked keys change,
 220           * * update the list:
 221           * * re-check if the new keys can send
 222           * * re-order api keys (trusted take preference)
 223           * * move expired keys to the bottom of the list
 224           */
 225  
 226          let cancelled = false;
 227          const update = async () => {
 228              const {
 229                  publicKeys,
 230                  trustedFingerprints,
 231                  obsoleteFingerprints,
 232                  compromisedFingerprints,
 233                  encryptionCapableFingerprints,
 234              } = model;
 235              const apiKeys = sortApiKeys({
 236                  keys: publicKeys.apiKeys,
 237                  trustedFingerprints,
 238                  obsoleteFingerprints,
 239                  compromisedFingerprints,
 240              });
 241              const pinnedKeys = sortPinnedKeys({
 242                  keys: model.isPGPExternal ? getPinnedKeys(model) : publicKeys.pinnedKeys,
 243                  obsoleteFingerprints,
 244                  compromisedFingerprints,
 245                  encryptionCapableFingerprints,
 246              });
 247              const verifyingPinnedKeys = getVerifyingKeys(pinnedKeys, compromisedFingerprints);
 248              const { encrypt } = await getContactPublicKeyModel({
 249                  emailAddress,
 250                  apiKeysConfig,
 251                  pinnedKeysConfig: { ...pinnedKeysConfig, pinnedKeys },
 252              });
 253              if (cancelled) {
 254                  return;
 255              }
 256              setModel((model?: ContactPublicKeyModel) => {
 257                  if (!model) {
 258                      return;
 259                  }
 260                  return {
 261                      ...model,
 262                      encrypt: pinnedKeysConfig === pinnedKeysConfigRef.current ? encrypt : model.encrypt,
 263                      publicKeys: { apiKeys, pinnedKeys, verifyingPinnedKeys },
 264                  };
 265              });
 266          };
 267          void withLoadingPgpSettings(update());
 268          return () => {
 269              cancelled = true;
 270          };
 271      }, [
 272          model?.trustedFingerprints,
 273          model?.obsoleteFingerprints,
 274          model?.encryptionCapableFingerprints,
 275          model?.compromisedFingerprints,
 276      ]);
 277  
 278      useEffect(() => {
```

<a id="source-2"></a>

## I2：金鑰能力檢查

完整檔案：`sources/proton-untrusted-keys/I2/packages/shared/lib/keys/publicKeys.ts`；摘錄行號：116–152。

SHA-256：`e83a4c3f4e916a62ba8e3b031c141d6acdf2b75e05c8759d932ef2b25902c99a`。

```text
 116  
 117  /**
 118   * Given a public key, return true if it is capable of encrypting messages.
 119   * This includes checking that the key is neither expired nor revoked.
 120   */
 121  export const getKeyEncryptionCapableStatus = async (publicKey: PublicKeyReference, timestamp?: number) => {
 122      const now = timestamp || +serverTime();
 123      return CryptoProxy.canKeyEncrypt({ key: publicKey, date: new Date(now) });
 124  };
 125  
 126  /**
 127   * Check if a public key is valid for sending according to the information stored in a public key model
 128   * We rely only on the fingerprint of the key to do this check
 129   */
 130  export const getIsValidForSending = (fingerprint: string, publicKeyModel: PublicKeyModel | ContactPublicKeyModel) => {
 131      const { compromisedFingerprints, obsoleteFingerprints, encryptionCapableFingerprints } = publicKeyModel;
 132      return (
 133          !compromisedFingerprints.has(fingerprint) &&
 134          !obsoleteFingerprints.has(fingerprint) &&
 135          encryptionCapableFingerprints.has(fingerprint)
 136      );
 137  };
 138  
 139  const getIsValidForVerifying = (fingerprint: string, compromisedFingerprints: Set<string>) => {
 140      return !compromisedFingerprints.has(fingerprint);
 141  };
 142  
 143  export const getVerifyingKeys = (keys: PublicKeyReference[], compromisedFingerprints: Set<string>) => {
 144      return keys.filter((key) => getIsValidForVerifying(key.getFingerprint(), compromisedFingerprints));
 145  };
 146  
 147  /**
 148   * For a given email address and its corresponding public keys (retrieved from the API and/or the corresponding vCard),
 149   * construct the contact public key model, which reflects the content of the vCard.
 150   */
 151  export const getContactPublicKeyModel = async ({
 152      emailAddress,
```

<a id="source-3"></a>

## I1：同步偏好選擇

完整檔案：`sources/proton-untrusted-keys/I1/packages/shared/lib/keys/publicKeys.ts`；摘錄行號：140–177。

SHA-256：`0c011a3bd078d996d5366d21cc7ebbcc7a023aec977dc8bbad19041283aacccb`。

```text
 140      return !compromisedFingerprints.has(fingerprint);
 141  };
 142  
 143  export const getVerifyingKeys = (keys: PublicKeyReference[], compromisedFingerprints: Set<string>) => {
 144      return keys.filter((key) => getIsValidForVerifying(key.getFingerprint(), compromisedFingerprints));
 145  };
 146  
 147  export const getContactEncryptionPreference = ({
 148      publicKeys,
 149      isPGPExternal,
 150      encryptToPinned,
 151      encryptToUntrusted,
 152  }: Pick<ContactPublicKeyModel, 'publicKeys' | 'isPGPExternal' | 'encryptToPinned' | 'encryptToUntrusted'>) => {
 153      if (publicKeys.pinnedKeys.length) {
 154          return encryptToPinned ?? true;
 155      }
 156      if (isPGPExternal && publicKeys.apiKeys.length) {
 157          return encryptToUntrusted ?? true;
 158      }
 159  };
 160  
 161  /**
 162   * For a given email address and its corresponding public keys (retrieved from the API and/or the corresponding vCard),
 163   * construct the contact public key model, which reflects the content of the vCard.
 164   */
 165  export const getContactPublicKeyModel = async ({
 166      emailAddress,
 167      apiKeysConfig,
 168      pinnedKeysConfig,
 169  }: Omit<PublicKeyConfigs, 'mailSettings'>): Promise<ContactPublicKeyModel> => {
 170      const {
 171          pinnedKeys = [],
 172          encryptToPinned,
 173          encryptToUntrusted,
 174          sign,
 175          scheme: vcardScheme,
 176          mimeType: vcardMimeType,
 177          isContact,
```

<a id="source-4"></a>

## D1：巢狀值與加總計數

完整檔案：`sources/clap-2297/D1/src/parse/matches/matched_arg.rs`；摘錄行號：10–41。

SHA-256：`42667f9e47737813d186f1a3819d8307a909a9be3cb1ab90d2ce887ff215223e`。

```text
  10  }
  11  
  12  #[derive(Debug, Clone, PartialEq, Eq)]
  13  pub(crate) struct MatchedArg {
  14      pub(crate) occurs: u64,
  15      pub(crate) ty: ValueType,
  16      pub(crate) indices: Vec<usize>,
  17      pub(crate) vals: Vec<Vec<OsString>>,
  18  }
  19  
  20  impl MatchedArg {
  21      pub(crate) fn new(ty: ValueType) -> Self {
  22          MatchedArg {
  23              occurs: 0,
  24              ty,
  25              indices: Vec::new(),
  26              vals: Vec::new(),
  27          }
  28      }
  29      pub(crate) fn contains_val(&self, val: &str) -> bool {
  30          self.values()
  31              .any(|v| OsString::as_os_str(v) == OsStr::new(val))
  32      }
  33  
  34      pub(crate) fn values(&self) -> std::iter::Flatten<std::slice::Iter<'_, Vec<OsString>>> {
  35          self.vals.iter().flatten()
  36      }
  37  
  38      pub(crate) fn num_vals(&self) -> usize {
  39          self.vals.iter().map(Vec::len).sum()
  40      }
  41  }
```

<a id="source-5"></a>

## D1：迭代器剩餘數量

完整檔案：`sources/clap-2297/D1/src/parse/matches/arg_matches.rs`；摘錄行號：1001–1071。

SHA-256：`d9c140945bab758fd8eaff1d522c0a697480981a238b83ad8c64fcc16e1d3398`。

```text
1001  /// assert_eq!(values.next(), None);
1002  /// ```
1003  /// [`ArgMatches::values_of`]: ./struct.ArgMatches.html#method.values_of
1004  #[derive(Clone)]
1005  #[allow(missing_debug_implementations)]
1006  pub struct Values<'a> {
1007      iter: Map<std::iter::Flatten<Iter<'a, Vec<OsString>>>, fn(&'a OsString) -> &'a str>,
1008      remaining: usize,
1009  }
1010  
1011  /// An iterator over the UTF-8 values belonging to each occurrence of an argument.
1012  ///
1013  /// Created by [`ArgMatches::grouped_values_of`]. Each item contains one
1014  /// occurrence's values, in their original order.
1015  #[derive(Clone, Debug)]
1016  pub struct GroupedValues<'a> {
1017      iter: Iter<'a, Vec<OsString>>,
1018  }
1019  
1020  impl<'a> GroupedValues<'a> {
1021      fn group(values: &'a Vec<OsString>) -> Vec<&'a str> {
1022          values
1023              .iter()
1024              .map(|value| value.to_str().expect(INVALID_UTF8))
1025              .collect()
1026      }
1027  }
1028  
1029  impl<'a> Iterator for GroupedValues<'a> {
1030      type Item = Vec<&'a str>;
1031  
1032      fn next(&mut self) -> Option<Self::Item> {
1033          self.iter.next().map(Self::group)
1034      }
1035  
1036      fn size_hint(&self) -> (usize, Option<usize>) {
1037          self.iter.size_hint()
1038      }
1039  }
1040  
1041  impl DoubleEndedIterator for GroupedValues<'_> {
1042      fn next_back(&mut self) -> Option<Self::Item> {
1043          self.iter.next_back().map(Self::group)
1044      }
1045  }
1046  
1047  impl ExactSizeIterator for GroupedValues<'_> {}
1048  
1049  impl<'a> Iterator for Values<'a> {
1050      type Item = &'a str;
1051  
1052      fn next(&mut self) -> Option<&'a str> {
1053          let value = self.iter.next()?;
1054          self.remaining -= 1;
1055          Some(value)
1056      }
1057      fn size_hint(&self) -> (usize, Option<usize>) {
1058          (self.remaining, Some(self.remaining))
1059      }
1060  }
1061  
1062  impl<'a> DoubleEndedIterator for Values<'a> {
1063      fn next_back(&mut self) -> Option<&'a str> {
1064          let value = self.iter.next_back()?;
1065          self.remaining -= 1;
1066          Some(value)
1067      }
1068  }
1069  
1070  impl<'a> ExactSizeIterator for Values<'a> {}
1071  
```

<a id="source-6"></a>

## E1：集中維護群組範圍

完整檔案：`sources/clap-2297/E1/src/parse/arg_matcher.rs`；摘錄行號：118–154。

SHA-256：`953d2e525c76d46fb681ffbfe2fe661868b2fea3dca064d7ea90129ee8431e10`。

```text
 118          debug!("ArgMatcher::inc_occurrence_of: arg={:?}", arg);
 119          let ma = self
 120              .entry(arg)
 121              .or_insert(MatchedArg::new(ValueType::CommandLine));
 122          ma.occurs += 1;
 123      }
 124  
 125      pub(crate) fn add_val_to(&mut self, arg: &Id, val: OsString, ty: ValueType) {
 126          // We will manually inc occurrences later(for flexibility under
 127          // specific circumstances, like only add one occurrence for flag
 128          // when we met: `--flag=one,two`).
 129          let ma = self.entry(arg).or_insert(MatchedArg::new(ty));
 130          if ma.val_groups.is_empty() {
 131              ma.val_groups.push(0..0);
 132          }
 133          ma.vals.push(val);
 134          ma.val_groups.last_mut().unwrap().end = ma.vals.len();
 135      }
 136  
 137      pub(crate) fn new_val_group(&mut self, arg: &Id) {
 138          let ma = self
 139              .entry(arg)
 140              .or_insert(MatchedArg::new(ValueType::CommandLine));
 141          ma.val_groups.push(ma.vals.len()..ma.vals.len());
 142      }
 143  
 144      pub(crate) fn add_index_to(&mut self, arg: &Id, idx: usize, ty: ValueType) {
 145          let ma = self.entry(arg).or_insert(MatchedArg::new(ty));
 146          ma.indices.push(idx);
 147      }
 148  
 149      pub(crate) fn needs_more_vals(&self, o: &Arg) -> bool {
 150          debug!("ArgMatcher::needs_more_vals: o={}", o.name);
 151          if let Some(ma) = self.get(&o.id) {
 152              if let Some(num) = o.num_vals {
 153                  debug!("ArgMatcher::needs_more_vals: num_vals...{}", num);
 154                  return if o.is_set(ArgSettings::MultipleValues) {
```

<a id="source-7"></a>

## F1：從快取列舉作品

完整檔案：`sources/openlibrary-index-state/F1/openlibrary/solr/data_provider.py`；摘錄行號：281–317。

SHA-256：`d18b05a43fa43ef10b6041c0c51b5d01f31ef78e22bfd64ae2b9bee64a467ace`。

```text
 281          """
 282  
 283          :param dict work: work object
 284          :rtype: list of dict
 285          """
 286          raise NotImplementedError()
 287  
 288      def get_works_of_author(self, author_key: str) -> list[dict]:
 289          """Find an author's works among documents already held in memory.
 290  
 291          Providers with another document store can override this operation.
 292          No Solr lookup is needed to build an author's local search data.
 293          """
 294          documents = getattr(self, 'cache', None)
 295          if documents is None:
 296              documents = getattr(self, 'docs_by_key', {})
 297          works = []
 298          for document in documents.values():
 299              if not document or document.get('type', {}).get('key') != '/type/work':
 300                  continue
 301              for role in document.get('authors', []):
 302                  author = role.get('author')
 303                  key = author.get('key') if isinstance(author, dict) else author
 304                  if key == author_key:
 305                      works.append(document)
 306                      break
 307          return works
 308  
 309      def get_work_ratings(self, work_key: str) -> WorkRatingsSummary | None:
 310          raise NotImplementedError()
 311  
 312      def get_work_reading_log(self, work_key: str) -> WorkReadingLogSolrSummary | None:
 313          raise NotImplementedError()
 314  
 315      def clear_cache(self):
 316          self.ia_cache.clear()
 317  
```

<a id="source-8"></a>

## F1：兩條作者統計路徑

完整檔案：`sources/openlibrary-index-state/F1/openlibrary/solr/update_work.py`；摘錄行號：1343–1480。

SHA-256：`e6585f1c2d305d55301402fe0dc3641cf4ed52846eef18dee82426729450cabc`。

```text
1343                          f'/works/ia:{iaid}' for iaid in solr_doc.get('ia') or []
1344                      )
1345                      state.adds.append(solr_doc)
1346          else:
1347              logger.error('unrecognized type while updating work %s', wkey)
1348          return state
1349  
1350  
1351  class AuthorSolrUpdater(AbstractSolrUpdater):
1352      key_prefix = '/authors/'
1353  
1354      def __init__(self, handle_redirects: bool = True, enrich: bool = False):
1355          self.handle_redirects = handle_redirects
1356          self.enrich = enrich
1357  
1358      async def update_key(self, thing: dict) -> SolrUpdateState:
1359          if state := self._deletion_state(thing):
1360              return state
1361  
1362          akey = thing['key']
1363          m = re_author_key.match(akey)
1364          if not m:
1365              logger.error('bad key: %s', akey)
1366          assert m
1367          author_id = m.group(1)
1368          try:
1369              assert thing['type']['key'] == '/type/author'
1370          except AssertionError:
1371              logger.error('AssertionError: %s', thing['type']['key'])
1372              raise
1373  
1374          doc = cast(SolrDocument, {'key': akey, 'type': 'author'})
1375          for name in ('name', 'alternate_names', 'birth_date', 'death_date', 'date'):
1376              if thing.get(name):
1377                  doc[name] = thing[name]
1378          self._derive_document(doc, akey)
1379          state = SolrUpdateState(keys=[akey], adds=[doc])
1380          if self.enrich:
1381              try:
1382                  await self._enrich_document(doc, author_id)
1383              except (HTTPError, ValueError, KeyError, TypeError):
1384                  logger.warning('Failed to enrich author %s', akey, exc_info=True)
1385          if self.handle_redirects:
1386              state.deletes.extend(data_provider.find_redirects(akey))
1387          return state
1388  
1389      def _derive_document(self, doc: SolrDocument, author_key: str) -> None:
1390          """Build search statistics from the provider's associated works."""
1391          works = data_provider.get_works_of_author(author_key)
1392          doc['work_count'] = len(works)
1393          subjects: dict[tuple[str, str], int] = defaultdict(int)
1394          ranked_works = []
1395          for work in works:
1396              editions = (
1397                  work['editions']
1398                  if 'editions' in work
1399                  else data_provider.get_editions_of_work(work)
1400              )
1401              ranked_works.append((len(editions), work, editions))
1402              for facet, names in get_work_subjects(work).items():
1403                  for name in names:
1404                      subjects[facet, name] += 1
1405          doc['top_subjects'] = [
1406              name
1407              for count, name in sorted(
1408                  ((count, name) for (facet, name), count in subjects.items()),
1409                  reverse=True,
1410              )[:10]
1411          ]
1412          top = max(ranked_works, key=lambda entry: entry[0], default=None)
1413          if top is not None:
1414              _, work, editions = top
1415              title = work.get('title') or next(
1416                  (edition['title'] for edition in editions if edition.get('title')),
1417                  None,
1418              )
1419              if title:
1420                  if work.get('subtitle'):
1421                      title += ': ' + work['subtitle']
1422                  doc['top_work'] = title
1423  
1424      async def _enrich_document(self, doc: SolrDocument, author_id: str) -> None:
1425          """Optionally supplement an author document with existing Solr statistics."""
1426          facet_fields = ['subject', 'time', 'person', 'place']
1427          base_url = get_solr_base_url() + '/select'
1428          async with httpx.AsyncClient() as client:
1429              response = await client.get(
1430                  base_url,
1431                  params=[  # type: ignore[arg-type]
1432                      ('wt', 'json'),
1433                      ('json.nl', 'arrarr'),
1434                      ('q', 'author_key:%s' % author_id),
1435                      ('sort', 'edition_count desc'),
1436                      ('rows', 1),
1437                      ('fl', 'title,subtitle'),
1438                      ('facet', 'true'),
1439                      ('facet.mincount', 1),
1440                  ]
1441                  + [('facet.field', '%s_facet' % f) for f in facet_fields],
1442              )
1443              reply = response.json()
1444  
1445          work_count = reply['response']['numFound']
1446          docs = reply['response'].get('docs', [])
1447          top_work = None
1448          if docs and docs[0].get('title'):
1449              top_work = docs[0]['title']
1450              if docs[0].get('subtitle'):
1451                  top_work += ': ' + docs[0]['subtitle']
1452          all_subjects = []
1453          for f in facet_fields:
1454              for subject, count in reply['facet_counts']['facet_fields'][f + '_facet']:
1455                  all_subjects.append((count, subject))
1456          all_subjects.sort(reverse=True)
1457          top_subjects = [subject for count, subject in all_subjects[:10]]
1458          if top_work:
1459              doc['top_work'] = top_work
1460          doc['work_count'] = work_count
1461          doc['top_subjects'] = top_subjects
1462  
1463  
1464  async def update_work(work: dict) -> list[SolrUpdateRequest]:
1465      """Compatibility interface returning requests for a work or orphan edition."""
1466      return (await WorkSolrUpdater().update_key(work))._to_requests()
1467  
1468  
1469  async def update_author(
1470      akey, a=None, handle_redirects=True
1471  ) -> list[SolrUpdateRequest] | None:
1472      """Compatibility interface returning requests for an author key."""
1473      if akey == '/authors/':
1474          return None
1475      if not a:
1476          a = await data_provider.get_document(akey)
1477      if not a.get('name'):
1478          return [DeleteRequest([akey])]
1479      state = await AuthorSolrUpdater(handle_redirects, enrich=True).update_key(a)
1480      return state._to_requests()
```

<a id="source-9"></a>

## F2：較廣的例外攔截

完整檔案：`sources/ansible-type-tags/F2/lib/ansible/config/manager.py`；摘錄行號：102–219。

SHA-256：`f8b6b4474aff75a92ea20a4a655bec07ccc5cb51cf8ba2e954d3d9e4f6bf8150`。

```text
 102      basedir = None
 103      if origin and os.path.isabs(origin) and os.path.exists(to_bytes(origin)):
 104          basedir = origin
 105  
 106      if value_type:
 107          value_type = value_type.lower()
 108  
 109      try:
 110          if value_type in ('boolean', 'bool'):
 111              if isinstance(value, bytes):
 112                  raise ValueError
 113              try:
 114                  value = boolean(value, strict=False)
 115              except TypeError:  # Non-strict conversion also treats unhashable values as false.
 116                  value = False
 117  
 118          elif value_type in ('integer', 'int'):
 119              if not isinstance(value, int) or isinstance(value, bool):
 120                  decimal_value = decimal.Decimal(value)
 121                  int_part = int(decimal_value)
 122                  if decimal_value != int_part:
 123                      raise ValueError
 124                  value = int_part
 125  
 126          elif value_type == 'float':
 127              if isinstance(value, bytes):
 128                  raise ValueError
 129              if not isinstance(value, float):
 130                  value = float(value)
 131  
 132          elif value_type == 'list':
 133              if isinstance(value, string_types):
 134                  value = [AnsibleTagHelper.tag_copy(value, unquote(x.strip())) for x in value.split(',')]
 135              elif isinstance(value, Sequence) and not isinstance(value, bytes):
 136                  if not isinstance(value, list):
 137                      value = list(value)
 138              else:
 139                  raise ValueError
 140  
 141          elif value_type == 'none':
 142              if isinstance(value, string_types) and value == 'None':
 143                  value = None
 144              else:
 145                  raise ValueError
 146  
 147          elif value_type == 'path':
 148              if isinstance(value, string_types):
 149                  value = resolve_path(value, basedir=basedir)
 150              else:
 151                  raise ValueError
 152  
 153          elif value_type in ('tmp', 'temppath', 'tmppath'):
 154              if isinstance(value, string_types):
 155                  value = resolve_path(value, basedir=basedir)
 156                  if not os.path.exists(value):
 157                      makedirs_safe(value, 0o700)
 158                  prefix = 'ansible-local-%s' % os.getpid()
 159                  value = tempfile.mkdtemp(prefix=prefix, dir=value)
 160                  atexit.register(cleanup_tmp_file, value, warn=True)
 161                  return value  # This newly created path must not inherit the base path's tags.
 162              else:
 163                  raise ValueError
 164  
 165          elif value_type in ('pathspec', 'pathlist'):
 166              if isinstance(value, string_types):
 167                  if value_type == 'pathspec':
 168                      items = value.split(os.pathsep)
 169                  else:
 170                      items = [x.strip() for x in value.split(',')]
 171                  value = [AnsibleTagHelper.tag_copy(value, x) for x in items]
 172              elif not isinstance(value, Sequence) or isinstance(value, bytes):
 173                  raise ValueError
 174  
 175              if any(not isinstance(x, string_types) for x in value):
 176                  raise ValueError
 177              value = [AnsibleTagHelper.tag_copy(x, resolve_path(x, basedir=basedir)) for x in value]
 178  
 179          elif value_type in ('dict', 'dictionary'):
 180              if not isinstance(value, Mapping):
 181                  raise ValueError
 182              if not isinstance(value, dict):
 183                  value = dict(value)
 184  
 185          elif value_type in ('str', 'string'):
 186              if isinstance(value, (string_types, bool, int, float, complex)):
 187                  value = to_text(value, errors='surrogate_or_strict')
 188              else:
 189                  raise ValueError
 190      except (TypeError, ValueError, OverflowError, decimal.DecimalException):
 191          raise ValueError(f'Invalid value provided for {value_type!r}: {original_value!r}') from None
 192  
 193      if isinstance(value, string_types) and origin_ftype == 'ini':
 194          value = unquote(value)
 195  
 196      if value is original_value:
 197          return original_value
 198      if AnsibleTagHelper.base_type(value) is AnsibleTagHelper.base_type(original_value) and value == original_value:
 199          return original_value
 200  
 201      return AnsibleTagHelper.tag_copy(original_value, value)
 202  
 203  
 204  # FIXME: see if this can live in utils/path
 205  def resolve_path(path, basedir=None):
 206      """ resolve relative or 'variable' paths """
 207      if '{{CWD}}' in path:  # allow users to force CWD using 'magic' {{CWD}}
 208          path = path.replace('{{CWD}}', os.getcwd())
 209  
 210      return unfrackpath(path, follow=False, basedir=basedir)
 211  
 212  
 213  # FIXME: generic file type?
 214  def get_config_type(cfile):
 215  
 216      ftype = None
 217      if cfile is not None:
 218          ext = os.path.splitext(cfile)[-1]
 219          if ext in ('.ini', '.cfg'):
```

<a id="source-10"></a>

## E2：局部失敗與轉換處理

完整檔案：`sources/ansible-type-tags/E2/lib/ansible/config/manager.py`；摘錄行號：95–131。

SHA-256：`1e4c1eff1c0e5d581207e73c9bcfad395c3238ddff8be13895d970a5a8bcf6c8`。

```text
  95          :string: Same as 'str'
  96      """
  97  
  98      if value is None:
  99          return value
 100  
 101      original_value = value
 102      invalid = False
 103      basedir = None
 104      if origin and os.path.isabs(origin) and os.path.exists(to_bytes(origin)):
 105          basedir = origin
 106  
 107      if value_type:
 108          value_type = value_type.lower()
 109  
 110      if value_type in ('boolean', 'bool'):
 111          if isinstance(value, bytes):
 112              invalid = True
 113          else:
 114              try:
 115                  value = boolean(value, strict=False)
 116              except TypeError:
 117                  # The standard converter uses set membership, which rejects unhashable values.
 118                  value = False
 119  
 120      elif value_type in ('integer', 'int'):
 121          if isinstance(value, bool):
 122              value = int(value)
 123          elif isinstance(value, bytes):
 124              invalid = True
 125          elif not isinstance(value, int):
 126              try:
 127                  if (decimal_value := decimal.Decimal(value)) == (int_part := int(decimal_value)):
 128                      value = int_part
 129                  else:
 130                      invalid = True
 131              except (decimal.DecimalException, TypeError, ValueError, OverflowError):
```

<a id="source-11"></a>

## I2：共用讀寫描述

完整檔案：`sources/flipt-segments/I2/internal/ext/common.go`；摘錄行號：36–119。

SHA-256：`2685701c12438b90458cdc04d670ac494f338ccdce955bf2cfe7a2b9130df939`。

```text
  36  	Rank            uint            `yaml:"rank,omitempty"`
  37  	SegmentKeys     []string        `yaml:"segments,omitempty"`
  38  	SegmentOperator string          `yaml:"operator,omitempty"`
  39  	Distributions   []*Distribution `yaml:"distributions,omitempty"`
  40  }
  41  
  42  // ruleYAML keeps legacy rule fields readable while exporting a unified segment.
  43  type ruleYAML struct {
  44  	Segment         ruleSegment     `yaml:"segment,omitempty"`
  45  	Rank            uint            `yaml:"rank,omitempty"`
  46  	SegmentKeys     []string        `yaml:"segments,omitempty"`
  47  	SegmentOperator string          `yaml:"operator,omitempty"`
  48  	Distributions   []*Distribution `yaml:"distributions,omitempty"`
  49  }
  50  
  51  type ruleSegment struct {
  52  	Key      string   `yaml:"-"`
  53  	Keys     []string `yaml:"keys"`
  54  	Operator string   `yaml:"operator"`
  55  }
  56  
  57  func (s ruleSegment) MarshalYAML() (interface{}, error) {
  58  	if s.Key != "" {
  59  		return s.Key, nil
  60  	}
  61  	if len(s.Keys) == 1 {
  62  		return s.Keys[0], nil
  63  	}
  64  	if s.Operator == "" {
  65  		s.Operator = flipt.SegmentOperator_OR_SEGMENT_OPERATOR.String()
  66  	}
  67  	type segmentObject ruleSegment
  68  	return segmentObject(s), nil
  69  }
  70  
  71  func (s *ruleSegment) UnmarshalYAML(unmarshal func(interface{}) error) error {
  72  	var key string
  73  	if err := unmarshal(&key); err == nil {
  74  		*s = ruleSegment{Key: key}
  75  		return nil
  76  	}
  77  	type segmentObject ruleSegment
  78  	var object segmentObject
  79  	if err := unmarshal(&object); err != nil {
  80  		return err
  81  	}
  82  	*s = ruleSegment(object)
  83  	return nil
  84  }
  85  
  86  func (r Rule) MarshalYAML() (interface{}, error) {
  87  	return ruleYAML{
  88  		Segment: ruleSegment{
  89  			Key:      r.SegmentKey,
  90  			Keys:     r.SegmentKeys,
  91  			Operator: r.SegmentOperator,
  92  		},
  93  		Rank:          r.Rank,
  94  		Distributions: r.Distributions,
  95  	}, nil
  96  }
  97  
  98  func (r *Rule) UnmarshalYAML(unmarshal func(interface{}) error) error {
  99  	var decoded ruleYAML
 100  	if err := unmarshal(&decoded); err != nil {
 101  		return err
 102  	}
 103  	keys, operator := decoded.SegmentKeys, decoded.SegmentOperator
 104  	if decoded.Segment.Keys != nil {
 105  		if len(keys) > 0 {
 106  			return fmt.Errorf("rule cannot have both segment.keys and segments")
 107  		}
 108  		keys, operator = decoded.Segment.Keys, decoded.Segment.Operator
 109  	}
 110  	if decoded.Segment.Key != "" || len(keys) == 1 || operator == "" {
 111  		operator = flipt.SegmentOperator_OR_SEGMENT_OPERATOR.String()
 112  	}
 113  	*r = Rule{
 114  		SegmentKey:      decoded.Segment.Key,
 115  		SegmentKeys:     keys,
 116  		SegmentOperator: operator,
 117  		Rank:            decoded.Rank,
 118  		Distributions:   decoded.Distributions,
 119  	}
```

<a id="source-12"></a>

## C2：限制輸出欄位

完整檔案：`sources/flipt-segments/C2/internal/ext/common.go`；摘錄行號：59–119。

SHA-256：`d04a9fc27bb46c66129a41812c83ab31dfd6822d748729750be493a796eda3bb`。

```text
  59  	if err := unmarshal(&group); err != nil {
  60  		return err
  61  	}
  62  	*s = ruleSegment(group)
  63  	return nil
  64  }
  65  
  66  func (r Rule) MarshalYAML() (interface{}, error) {
  67  	var segment interface{}
  68  	switch {
  69  	case r.SegmentKey != "":
  70  		segment = r.SegmentKey
  71  	case len(r.SegmentKeys) == 1:
  72  		segment = r.SegmentKeys[0]
  73  	case len(r.SegmentKeys) > 1:
  74  		operator := r.SegmentOperator
  75  		if operator == "" {
  76  			operator = flipt.SegmentOperator_OR_SEGMENT_OPERATOR.String()
  77  		}
  78  		segment = ruleSegment{Keys: r.SegmentKeys, Operator: operator}
  79  	}
  80  
  81  	return struct {
  82  		Segment       interface{}     `yaml:"segment,omitempty"`
  83  		Rank          uint            `yaml:"rank,omitempty"`
  84  		Distributions []*Distribution `yaml:"distributions,omitempty"`
  85  	}{segment, r.Rank, r.Distributions}, nil
  86  }
  87  
  88  func (r *Rule) UnmarshalYAML(unmarshal func(interface{}) error) error {
  89  	var decoded struct {
  90  		Segment       ruleSegment     `yaml:"segment,omitempty"`
  91  		Rank          uint            `yaml:"rank,omitempty"`
  92  		Segments      []string        `yaml:"segments,omitempty"`
  93  		Operator      string          `yaml:"operator,omitempty"`
  94  		Distributions []*Distribution `yaml:"distributions,omitempty"`
  95  	}
  96  	if err := unmarshal(&decoded); err != nil {
  97  		return err
  98  	}
  99  	if len(decoded.Segment.Keys) > 0 && len(decoded.Segments) > 0 {
 100  		return fmt.Errorf("rule cannot have both segment.keys and segments")
 101  	}
 102  
 103  	*r = Rule{
 104  		SegmentKey:      decoded.Segment.Key,
 105  		SegmentKeys:     decoded.Segments,
 106  		SegmentOperator: decoded.Operator,
 107  		Rank:            decoded.Rank,
 108  		Distributions:   decoded.Distributions,
 109  	}
 110  	if len(decoded.Segment.Keys) > 0 {
 111  		r.SegmentKeys = decoded.Segment.Keys
 112  		r.SegmentOperator = decoded.Segment.Operator
 113  	}
 114  	if r.SegmentKey != "" || len(r.SegmentKeys) == 1 {
 115  		r.SegmentOperator = flipt.SegmentOperator_OR_SEGMENT_OPERATOR.String()
 116  	}
 117  	return nil
 118  }
 119  
```

<a id="source-13"></a>

## C2：snapshot 單鍵正規化

完整檔案：`sources/flipt-segments/C2/internal/storage/fs/snapshot.go`；摘錄行號：343–379。

SHA-256：`8e722186ce5e696ddea57f9f4ec851d9c0f9d89ea009adcfbcbe9d4715677de0`。

```text
 343  					Constraints: evc,
 344  				}
 345  			}
 346  
 347  			segmentOperator := flipt.SegmentOperator_value[r.SegmentOperator]
 348  			if len(segmentKeys) == 1 {
 349  				segmentOperator = int32(flipt.SegmentOperator_OR_SEGMENT_OPERATOR)
 350  				rule.SegmentKey = segmentKeys[0]
 351  				rule.SegmentKeys = nil
 352  			}
 353  			evalRule.SegmentOperator = flipt.SegmentOperator(segmentOperator)
 354  			evalRule.Segments = segments
 355  
 356  			evalRules = append(evalRules, evalRule)
 357  
 358  			// Set segment operator on rule.
 359  			rule.SegmentOperator = flipt.SegmentOperator(segmentOperator)
 360  
 361  			for _, d := range r.Distributions {
 362  				variant, found := findByKey(d.VariantKey, flag.Variants...)
 363  				if !found {
 364  					continue
 365  				}
 366  
 367  				id := uuid.Must(uuid.NewV4()).String()
 368  				rule.Distributions = append(rule.Distributions, &flipt.Distribution{
 369  					Id:        id,
 370  					Rollout:   d.Rollout,
 371  					RuleId:    rule.Id,
 372  					VariantId: variant.Id,
 373  					CreatedAt: ss.now,
 374  					UpdatedAt: ss.now,
 375  				})
 376  
 377  				evalDists[evalRule.ID] = append(evalDists[evalRule.ID], &storage.EvaluationDistribution{
 378  					ID:                id,
 379  					Rollout:           d.Rollout,
```

<a id="source-14"></a>

## F2：額外 catch

完整檔案：`sources/element-sessions/F2/src/components/views/settings/tabs/user/SessionManagerTab.tsx`；摘錄行號：67–103。

SHA-256：`0398efb0fe97d73edab3dfa599f91276ce000a9087ae755abd5de448536916b8`。

```text
  67                  matrixClient,
  68                  deviceIds,
  69                  async (success) => {
  70                      try {
  71                          if (success) {
  72                              setSelectedDeviceIds(ids => ids.filter(deviceId => !deviceIds.includes(deviceId)));
  73                              await refreshDevices();
  74                          }
  75                      } catch (error) {
  76                          logger.error("Error refreshing sessions", error);
  77                      } finally {
  78                          clearSigningOutDevices();
  79                      }
  80                  },
  81              );
  82          } catch (error) {
  83              logger.error("Error deleting sessions", error);
  84              clearSigningOutDevices();
  85          }
  86      };
  87  
  88      return {
  89          onSignOutCurrentDevice,
  90          onSignOutOtherDevices,
  91          signingOutDeviceIds,
  92      };
  93  };
  94  
  95  const SessionManagerTab: React.FC = () => {
  96      const {
  97          devices,
  98          pushers,
  99          localNotificationSettings,
 100          currentDeviceId,
 101          isLoadingDeviceList,
 102          requestDeviceVerification,
 103          refreshDevices,
```

<a id="source-15"></a>

## I2：相同的 finally 清理

完整檔案：`sources/element-sessions/I2/src/components/views/settings/tabs/user/SessionManagerTab.tsx`；摘錄行號：66–102。

SHA-256：`30ccd2ab8b234d445ef89adb121bf0a721dbd43045f6bbbcf06b7da55fad8d1c`。

```text
  66                  async (success) => {
  67                      try {
  68                          if (success) {
  69                              setSelectedDeviceIds(ids => ids.filter(id => !deviceIds.includes(id)));
  70                              await refreshDevices();
  71                          }
  72                      } finally {
  73                          setSigningOutDeviceIds(ids => ids.filter(id => !deviceIds.includes(id)));
  74                      }
  75                  },
  76              );
  77          } catch (error) {
  78              logger.error("Error deleting sessions", error);
  79              setSigningOutDeviceIds(ids => ids.filter(id => !deviceIds.includes(id)));
  80          }
  81      };
  82  
  83      return {
  84          onSignOutCurrentDevice,
  85          onSignOutOtherDevices,
  86          signingOutDeviceIds,
  87      };
  88  };
  89  
  90  const SessionManagerTab: React.FC = () => {
  91      const {
  92          devices,
  93          pushers,
  94          localNotificationSettings,
  95          currentDeviceId,
  96          isLoadingDeviceList,
  97          requestDeviceVerification,
  98          refreshDevices,
  99          saveDeviceName,
 100          setPushNotifications,
 101          supportsMSC3881,
 102      } = useOwnDevices();
```

<a id="source-16"></a>

## 既有刷新函式：已承接一般失敗

完整檔案：`supporting-sources/element-sessions/src/components/views/settings/devices/useOwnDevices.ts`；摘錄行號：116–162。

SHA-256：`82a57781c31291636f00e6d72077395b986b6a4bb0ae6e7e512d599832a38199`。

```text
 116  
 117      useEffect(() => {
 118          matrixClient.doesServerSupportUnstableFeature("org.matrix.msc3881").then(hasSupport => {
 119              setSupportsMSC3881(hasSupport);
 120          });
 121      }, [matrixClient]);
 122  
 123      const refreshDevices = useCallback(async () => {
 124          setIsLoadingDeviceList(true);
 125          try {
 126              // realistically we should never hit this
 127              // but it satisfies types
 128              if (!userId) {
 129                  throw new Error('Cannot fetch devices without user id');
 130              }
 131              const devices = await fetchDevicesWithVerification(matrixClient, userId);
 132              setDevices(devices);
 133  
 134              const { pushers } = await matrixClient.getPushers();
 135              setPushers(pushers);
 136  
 137              const notificationSettings = new Map<string, LocalNotificationSettings>();
 138              Object.keys(devices).forEach((deviceId) => {
 139                  const eventType = `${LOCAL_NOTIFICATION_SETTINGS_PREFIX.name}.${deviceId}`;
 140                  const event = matrixClient.getAccountData(eventType);
 141                  if (event) {
 142                      notificationSettings.set(
 143                          deviceId,
 144                          event.getContent(),
 145                      );
 146                  }
 147              });
 148              setLocalNotificationSettings(notificationSettings);
 149  
 150              setIsLoadingDeviceList(false);
 151          } catch (error) {
 152              if ((error as MatrixError).httpStatus == 404) {
 153                  // 404 probably means the HS doesn't yet support the API.
 154                  setError(OwnDevicesError.Unsupported);
 155              } else {
 156                  logger.error("Error loading sessions:", error);
 157                  setError(OwnDevicesError.Default);
 158              }
 159              setIsLoadingDeviceList(false);
 160          }
 161      }, [matrixClient, userId]);
 162  
```

<a id="source-17"></a>

## 既有工具：未等待回呼

完整檔案：`supporting-sources/element-sessions/src/components/views/settings/devices/deleteDevices.tsx`；摘錄行號：34–70。

SHA-256：`2c5a187d29517f2d439e67d1aa157e01ecfa6c295238f8f7a04cf61d7e3af867`。

```text
  34  ) => {
  35      if (!deviceIds.length) {
  36          return;
  37      }
  38      try {
  39          await makeDeleteRequest(matrixClient, deviceIds)();
  40          // no interactive auth needed
  41          onFinished(true, undefined);
  42      } catch (error) {
  43          if (error.httpStatus !== 401 || !error.data?.flows) {
  44              // doesn't look like an interactive-auth failure
  45              throw error;
  46          }
  47  
  48          // pop up an interactive auth dialog
  49  
  50          const numDevices = deviceIds.length;
  51          const dialogAesthetics = {
  52              [SSOAuthEntry.PHASE_PREAUTH]: {
  53                  title: _t("Use Single Sign On to continue"),
  54                  body: _t("Confirm logging out these devices by using Single Sign On to prove your identity.", {
  55                      count: numDevices,
  56                  }),
  57                  continueText: _t("Single Sign On"),
  58                  continueKind: "primary",
  59              },
  60              [SSOAuthEntry.PHASE_POSTAUTH]: {
  61                  title: _t("Confirm signing out these devices", {
  62                      count: numDevices,
  63                  }),
  64                  body: _t("Click the button below to confirm signing out these devices.", {
  65                      count: numDevices,
  66                  }),
  67                  continueText: _t("Sign out devices", { count: numDevices }),
  68                  continueKind: "danger",
  69              },
  70          };
```
