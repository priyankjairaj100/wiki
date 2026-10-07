"""Verify complete actual reader execution against frozen identity and decoding."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--outputs', type=Path, required=True)
    p.add_argument('--jobs', type=Path, required=True)
    p.add_argument('--freeze', type=Path, default=ROOT / 'pass4/inference/provenance/primary_reader_freeze_final.json')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--manifest', type=Path)
    p.add_argument('--input', type=Path)
    p.add_argument('--server-log', type=Path)
    args = p.parse_args()
    frozen = json.loads(args.freeze.read_text())
    expected = {job['job_id'] for job in read(args.jobs)}
    outputs = read(args.outputs)
    actual = {row['id'] for row in outputs}
    manifest_path = args.manifest or args.outputs.with_suffix('.manifest.json')
    input_path = args.input or args.outputs.parent / 'reader_input.jsonl'
    server_log = args.server_log or args.outputs.with_suffix('.server.log')
    manifest = json.loads(manifest_path.read_text())
    assert manifest['output_sha256'] == sha(args.outputs)
    assert manifest['input_sha256'] == sha(input_path)
    assert manifest['output_rows'] == len(outputs) == manifest['rows']
    command = manifest['server_command']
    def flag(name):
        assert command.count(name) == 1, name
        return command[command.index(name) + 1]
    required_flags = {'-c': frozen['context_tokens'], '-t': frozen['threads'],
                      '-tb': frozen['batch_threads'], '-b': frozen['batch_tokens'],
                      '-ub': frozen['ubatch_tokens'], '--poll': frozen['poll'],
                      '--poll-batch': frozen['poll_batch'], '--parallel': frozen['parallel_slots'],
                      '--n-gpu-layers': frozen['gpu_layers'], '--seed': frozen['seed'],
                      '--temp': frozen['temperature']}
    for name, value in required_flags.items():
        assert flag(name) == str(value), (name, flag(name), value)
    for key, frozen_key in [('threads', 'threads'), ('context', 'context_tokens'),
                            ('batch', 'batch_tokens'), ('ubatch', 'ubatch_tokens')]:
        assert manifest[key] == frozen[frozen_key], key
    log = server_log.read_text()
    assert 'n_threads = ' + str(frozen['threads']) in log
    assert 'n_ctx_slot = ' + str(frozen['context_tokens']) in log
    token_path = args.outputs.with_suffix('.token_preflight.json')
    assert manifest['token_preflight_sha256'] == sha(token_path)
    preflight = json.loads(token_path.read_text())
    assert preflight['all_fit'] and preflight['context_tokens'] == frozen['context_tokens']
    assert preflight['max_reserved_tokens'] <= frozen['context_tokens']
    assert expected <= {row['id'] for row in preflight['counts']}
    assert all(row['reserved_with_margin'] <= frozen['context_tokens'] and row['max_tokens'] == frozen['max_tokens']
               for row in preflight['counts'])
    assert len(actual) == len(outputs) and actual == expected, 'Execution must complete every unique frozen job exactly once.'
    for row in outputs:
        request = row['request']
        assert request['model'] == frozen['model_repository']
        for key in ['temperature', 'seed', 'max_tokens', 'cache_prompt']:
            assert request[key] == frozen[key], (row['id'], key)
        assert request['stream'] is False
        assert 'response_format' not in request, 'Primary run has no JSON grammar.'
        for key in ['model_repository', 'model_revision', 'model_sha256', 'runtime_release']:
            assert row[key] == frozen[key], (row['id'], key)
        assert [message['role'] for message in request['messages']] == ['user']
        fingerprint = row['response'].get('system_fingerprint', '')
        assert frozen['runtime_release'] in fingerprint
        assert frozen['runtime_commit'][:9] in fingerprint
    result = {'all_checks_passed': True, 'unique_generations': len(outputs),
              'model_repository': frozen['model_repository'], 'model_revision': frozen['model_revision'],
              'runtime_release': frozen['runtime_release'],
              'actual_server_flags': required_flags, 'actual_server_log_matches': True,
              'all_prompts_fit_without_truncation': True,
              'max_reserved_tokens': preflight['max_reserved_tokens'],
              'unchanged_decoder': {key: frozen[key] for key in ['temperature', 'seed', 'max_tokens', 'cache_prompt']},
              'hashes': {str(path): sha(path) for path in [args.outputs, args.jobs, args.freeze, manifest_path, input_path, server_log, token_path, Path(__file__)]}}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
