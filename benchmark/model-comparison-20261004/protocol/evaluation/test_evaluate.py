"""Protect the failures that made earlier scores unstable."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import evaluate


class FixedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.root_patch=patch.object(evaluate,'ROOT',self.root)
        self.root_patch.start()
        case=self.root/'cases/example';case.mkdir(parents=True)
        (case/'task.md').write_text('Return the selected values.\n')
        self.write('cases.json',[{'id':'example','task_sha256':evaluate.digest(case/'task.md')}])
        self.write('cases/example/contract.json',{
            'requirements':[{'id':'C1','source_lines':[1],'source_text':'Return the selected values.','checks':['first','second']}],
            'checks':[{'id':'first'},{'id':'second'}],'unresolved':[]})
        self.delivery=self.root/'delivery.patch';self.delivery.write_text('saved delivery')
        self.write('manifest.json',{'version':'test','files':evaluate.inventory()})

    def tearDown(self):
        self.root_patch.stop();self.temp.cleanup()

    def write(self,path,value):
        (self.root/path).write_text(json.dumps(value),encoding='utf-8')

    def evidence(self,checks):
        return {'case':'example','patch_sha256':evaluate.digest(self.delivery),
                'evaluator_sha256':evaluate.verify(),'checks':checks}

    def test_all_registered_checks_are_required(self):
        self.assertEqual(evaluate.score('example',self.delivery,self.evidence({'first':'pass'}))['status'],'incomplete')
        self.assertEqual(evaluate.score('example',self.delivery,self.evidence({'first':'pass','second':'pass'}))['status'],'pass')

    def test_environment_fault_is_not_a_contract_failure(self):
        self.assertEqual(evaluate.score('example',self.delivery,self.evidence({'first':'pass','second':'environment_error'}))['status'],'incomplete')

    def test_extra_posthoc_check_cannot_change_the_score(self):
        with self.assertRaises(ValueError):
            evaluate.score('example',self.delivery,self.evidence({'first':'pass','second':'pass','new_probe':'fail'}))

    def test_wrong_delivery_is_rejected(self):
        record=self.evidence({'first':'pass','second':'pass'});record['patch_sha256']='different'
        with self.assertRaises(ValueError):evaluate.score('example',self.delivery,record)

    def test_changed_evaluator_is_rejected(self):
        (self.root/'new_test.py').write_text('changed grading')
        with self.assertRaises(ValueError):evaluate.verify()

    def test_old_result_cannot_be_overwritten(self):
        path=self.root/'result.json'
        evaluate.write_new(path,{'status':'pass'})
        with self.assertRaises(FileExistsError):evaluate.write_new(path,{'status':'fail'})
        self.assertEqual(evaluate.read(path),{'status':'pass'})

    def test_shared_failure_does_not_invent_clause_failures(self):
        result=evaluate.score('example',self.delivery,self.evidence({'first':'fail','second':'pass'}))
        self.assertEqual(result['status'],'fail')
        self.assertEqual(result['failed_checks'],['first'])
        self.assertNotIn('failed_requirements',result)

    def test_test_pass_without_execution_review_is_not_task_completion(self):
        result=evaluate.score('example',self.delivery,self.evidence({'first':'pass','second':'pass'}))
        self.assertEqual(result['status'],'pass')
        self.assertIsNone(result['task_completed'])

    def test_completion_requires_the_same_delivery_execution_record(self):
        record=self.evidence({'first':'pass','second':'pass'})
        record['execution_review']={'status':'pass','patch_sha256':evaluate.digest(self.delivery),'evidence':['recorded scope and run review']}
        self.assertTrue(evaluate.score('example',self.delivery,record)['task_completed'])
        record['execution_review']['patch_sha256']='another delivery'
        with self.assertRaises(ValueError):evaluate.score('example',self.delivery,record)


if __name__=='__main__':unittest.main()
