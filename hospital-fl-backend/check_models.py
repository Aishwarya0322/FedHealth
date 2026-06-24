import torch, os
expected = {'heart': 13, 'cancer': 23, 'anaemia': 5}
for f in sorted(os.listdir('.')):
    if f.startswith('global_model') and f.endswith('.pth'):
        sd = torch.load(f, map_location='cpu')
        dim = sd['fc1.weight'].shape[1]
        # figure out which disease this should be
        disease = None
        for d in expected:
            if d in f:
                disease = d
                break
        status = ''
        if disease:
            status = 'OK' if dim == expected[disease] else f'MISMATCH (expected {expected[disease]})'
        else:
            status = 'unknown disease'
        print(f'{f}: input_dim={dim}  disease={disease}  {status}')
