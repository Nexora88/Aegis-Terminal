def assess(s):
    score=0; signals=[]
    for key,label in [('cpu_percent','CPU'),('memory_percent','memory'),('disk_percent','disk')]:
        v=s.get(key,0)
        if v>=95: score+=25; signals.append(f'{label} utilization is extremely high.')
        elif v>=85: score+=10; signals.append(f'{label} utilization is elevated.')
    level='HIGH' if score>=50 else 'MEDIUM' if score>=20 else 'LOW'
    return {'risk_level':level,'score':min(score,100),'signals':signals}
