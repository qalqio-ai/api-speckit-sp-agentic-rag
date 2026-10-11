"""Present retained demo evidence with an explicit recording label."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    print('RECORDED LOCAL EVIDENCE — this command does not run a model or query.')
    print('Mode: constrained selection of reviewed claims; no unrestricted generation.')
    print('Artifact:', args.report)
    for case in report.get('cases', []):
        result = case.get('result', case)
        print('\nCase:', case['case_id'], 'status:', result['status'])
        if 'question' in case:
            print('Question:', case['question'])
        for claim in result.get('claims', []):
            print('Claim:', claim['text'])
            print('Supporting chunk IDs:', ', '.join(claim['chunk_ids']))
        for passage in result.get('citations', []):
            print('Evidence:', passage['text'])
            print('Provenance:', passage['use_case_id'], passage['source_id'], passage['revision'],
                  passage['chunk_id'], passage['content_sha256'], passage['start'], passage['end'])
        if result.get('reason'):
            print('Abstention reason:', result['reason'])
        print('Total seconds:', round(result.get('elapsed_ms', case.get('total_ms', 0))/1000, 2))
    print('\nCollection absent:', report.get('collection_absent'), 'stack absent:', report.get('stack_absent'))


if __name__ == '__main__':
    main()
