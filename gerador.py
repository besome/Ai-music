import random, sys, os
import wave
import numpy as np
import mido
from IPython.display import Audio, display
from music21 import stream, meter, tempo, note, chord, instrument

SUBESTILO = random.choice(['castelo','aquatico', 'heroico', 'santuario', 'chefe', 'caverna' ])
NOTAS = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
TOM = random.choice(NOTAS)
REPETICOES = 2
SEMENTE = None

random.seed(SEMENTE)
np.random.seed(SEMENTE)

INTERVALOS = {
    'maior': {'1':0, '2':2, 'b3':3, '3':4, '4':5, '5':7, '6':9, 'b7':10},
    'menor': {'1':0, '2':2, '3':3, '4':5, '5':7, '6':8, 'b7':10},
    'dim':   {'1':0, '2':2, '3':3, '4':5, '5':6, '6':9, 'b7':9},
    'sus2':  {'1':0, '2':2, '3':2, '4':5, '5':7, '6':8, 'b7':10},
}

def parse_acorde(nome):
    for sufixo, qualidade in (('sus2', 'sus2'), ('dim', 'dim'), ('m', 'menor')):
        if nome.endswith(sufixo):
            return nome[:-len(sufixo)], qualidade
    return nome, 'maior'

def graus_do_acorde(nome):
    fund, qualidade = parse_acorde(nome)
    base = NOTAS.index(fund)
    return {g: NOTAS[(base + st) % 12] for g, st in INTERVALOS[qualidade].items()}

def m21(nome, oitava):
    return nome[0] + nome[1:].replace('b', '-') + str(oitava)

def nota(grau, acorde, oitava_base):
    oitava = oitava_base + grau.count("'")
    grau = grau.rstrip("'")
    graus = graus_do_acorde(acorde)
    return m21(graus.get(grau, graus['1']), oitava)

def gerar(simbolo, regras):
    if simbolo not in regras:
        return [simbolo]
    opcoes, pesos = zip(*regras[simbolo])
    escolha = random.choices(opcoes, weights=pesos)[0]
    return [t for s in escolha.split() for t in gerar(s, regras)]

GRAUS_ACORDE = {
    'I': (0, ''), 'ii': (2, 'm'), 'iii': (4, 'm'), 'IV': (5, ''), 'V': (7, ''), 'vi': (9, 'm'),
    'i': (0, 'm'), 'iv': (5, 'm'), 'v': (7, 'm'),
    'bII': (1, ''), 'bIII': (3, ''), 'bV': (6, ''), 'bVI': (8, ''), 'bVII': (10, ''),
    'vii°': (11, 'dim'), 'ii°': (2, 'dim'),
    'isus2': (0, 'sus2'), 'bVIsus2': (8, 'sus2'), 'bVIIsus2': (10, 'sus2'),
}

def grau_para_acorde(grau, tom):
    st, sufixo = GRAUS_ACORDE[grau]
    return NOTAS[(NOTAS.index(tom) + st) % 12] + sufixo

HARMONIA = {
    'castelo': {
        'PECA':  [('FRASE FRASE FINAL', 1.0)],
        'FRASE': [('i bVI bVII i', 0.30), ('i iv V i', 0.30), ('i bVI iv V', 0.20), ('i vii° i V', 0.20)],
        'FINAL': [('bVI bVII i i', 0.5), ('iv V i i', 0.5)],
    },
    'caverna': {
        'PECA':  [('FRASE FRASE', 1.0)],
        'FRASE': [('isus2 isus2 bVIIsus2 isus2', 0.35), ('i bVI i bVI', 0.25),
                  ('isus2 bII isus2 i', 0.20), ('i iv i bVIIsus2', 0.20)],
    },
    'chefe': {
        'PECA':  [('FRASE FRASE FRASE FINAL', 1.0)],
        'FRASE': [('i bII i bII', 0.30), ('i bVI bV V', 0.25), ('i i bVI V', 0.25), ('i bIII bII i', 0.20)],
        'FINAL': [('bVI bV V V', 0.5), ('bII bII V V', 0.5)],
    },
    'santuario': {
        'PECA':  [('FRASE FINAL', 1.0)],
        'FRASE': [('I iii IV I', 0.30), ('I vi IV V', 0.30), ('I IV I V', 0.20), ('I bVII IV I', 0.20)],
        'FINAL': [('IV V I I', 0.6), ('IV iv I I', 0.4)],   
    },
    'heroico': {
        'PECA':  [('FRASE FRASE FINAL', 1.0)],
        'FRASE': [('I bVII IV I', 0.35), ('I V vi IV', 0.25), ('I bVI bVII I', 0.25), ('vi IV I V', 0.15)],
        'FINAL': [('bVI bVII I I', 0.6), ('IV V I I', 0.4)],
    },
    'aquatico': {
        'PECA':  [('FRASE FRASE', 1.0)],
        'FRASE': [('i IV i IV', 0.35), ('i ii i IV', 0.20), ('i bIII IV i', 0.25), ('i bVII IV i', 0.20)],
    },
}

MELODIA = {
    'castelo': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('ARPEJO', 0.25), ('ESCALA', 0.20),
                   ('FORTE 0.5 FRACA 0.25 FRACA 0.25 FORTE 1.0', 0.20),
                   ('FORTE 1.5 FRACA 0.5', 0.20), ('FORTE 0.75 FORTE 0.75 FRACA 0.5', 0.15)],
        'ARPEJO': [("1 0.25 3 0.25 5 0.25 1' 0.25 5 0.25 3 0.25 1 0.25 3 0.25", 0.5),
                   ("1 0.25 5 0.25 1' 0.25 5 0.25 3 0.25 5 0.25 1' 0.25 5 0.25", 0.5)],
        'ESCALA': [("1' 0.25 b7 0.25 6 0.25 5 0.25 4 0.25 3 0.25 2 0.25 1 0.25", 1.0)],
        'FORTE': [('1', 0.35), ('3', 0.30), ('5', 0.25), ("1'", 0.10)],
        'FRACA': [('2', 0.35), ('4', 0.20), ('5', 0.25), ('6', 0.20)],
    },
    'caverna': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('FORTE 2.0', 0.30), ('R 1.0 FORTE 1.0', 0.20), ('FORTE 1.5 FRACA 0.5', 0.20),
                   ('R 2.0', 0.15), ('FORTE 1.0 R 1.0', 0.15)],
        'FORTE': [('1', 0.30), ('5', 0.30), ("1'", 0.20), ('3', 0.20)],
        'FRACA': [('2', 0.40), ('6', 0.30), ('4', 0.30)],
    },
    'chefe': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('PEDAL', 0.30), ('FORTE 0.25 FORTE 0.25 FRACA 0.5 FORTE 0.5 FRACA 0.5', 0.25),
                   ('ARPEJO_DESC', 0.25), ('FORTE 0.5 FORTE 0.5 FORTE 1.0', 0.20)],
        'PEDAL': [("1 0.25 1' 0.25 1 0.25 b7 0.25 1 0.25 6 0.25 1 0.25 5 0.25", 1.0)],
        'ARPEJO_DESC': [("1' 0.25 5 0.25 3 0.25 1 0.25 5 0.25 3 0.25 1 0.25 R 0.25", 1.0)],
        'FORTE': [('1', 0.35), ("1'", 0.25), ('5', 0.25), ('3', 0.15)],
        'FRACA': [('2', 0.30), ('b7', 0.30), ('6', 0.20), ('4', 0.20)],
    },
    'santuario': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('FORTE 2.0', 0.30), ('FORTE 1.0 FRACA 1.0', 0.30),
                   ('FORTE 1.5 FRACA 0.5', 0.20), ('FORTE 1.0 R 1.0', 0.20)],
        'FORTE': [('3', 0.35), ('5', 0.30), ('1', 0.20), ("1'", 0.15)],
        'FRACA': [('2', 0.40), ('6', 0.40), ('5', 0.20)],
    },
    'heroico': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('FANFARRA', 0.30), ('FORTE 0.75 FRACA 0.25 FORTE 1.0', 0.30),
                   ('FORTE 1.0 FORTE 0.5 FRACA 0.5', 0.20), ('FORTE 2.0', 0.20)],
        'FANFARRA': [("1 0.5 5 0.5 1' 1.0", 0.5), ("5 0.75 5 0.25 1' 1.0", 0.5)],
        'FORTE': [('1', 0.30), ('5', 0.30), ('3', 0.25), ("1'", 0.15)],
        'FRACA': [('2', 0.40), ('6', 0.35), ('4', 0.25)],
    },
    'aquatico': {
        'MELODIA': [('METADE METADE', 1.0)],
        'METADE': [('FLUXO', 0.40), ('FORTE 1.0 FRACA 0.5 FRACA 0.5', 0.30), ('FORTE 1.5 FRACA 0.5', 0.30)],
        'FLUXO': [('1 0.5 2 0.5 3 0.5 5 0.5', 0.5), ('5 0.5 3 0.5 2 0.5 1 0.5', 0.5)],
        'FORTE': [('1', 0.30), ('3', 0.30), ('5', 0.30), ("1'", 0.10)],
        'FRACA': [('2', 0.35), ('4', 0.35), ('b7', 0.30)],
    },
}

SUBESTILOS = {
    'castelo': {
        'bpm': 150, 'arpejo': (['1', '3', '5', '3'], 0.25, 4),
        'baixo': [('1', 0.5), ("1'", 0.5)] * 4,
        'bateria': {'bumbo': 'x.......x.x.....', 'caixa': '....x.......x...', 'chimbal': 'x.x.x.x.x.x.x.x.'},
        'timbres': ('pulso25', 'pulso12'), 'gate': 0.85, 'eco': None, 'vibrato': 0.0, 'repetir': 0.6,
    },
    'caverna': {
        'bpm': 90, 'arpejo': (['1', '5', "1'", '5'], 0.5, 3),
        'baixo': [('1', 4.0)],
        'bateria': {'bumbo': 'x...............', 'caixa': '................', 'chimbal': '........x.......'},
        'timbres': ('pulso12', 'pulso12'), 'gate': 1.0, 'eco': (0.75, 0.4), 'vibrato': 0.004, 'repetir': 0.5,
    },
    'chefe': {
        'bpm': 180, 'arpejo': (['1', "1'", '5', "1'"], 0.25, 3),
        'baixo': [('1', 0.25), ('1', 0.25), ("1'", 0.25), ('1', 0.25)] * 4,
        'bateria': {'bumbo': 'x.x.x.x.x.x.x.x.', 'caixa': '....x.......x..x', 'chimbal': 'xxxxxxxxxxxxxxxx'},
        'timbres': ('pulso50', 'pulso25'), 'gate': 0.7, 'eco': None, 'vibrato': 0.0, 'repetir': 0.7,
    },
    'santuario': {
        'bpm': 80, 'arpejo': (['1', '3', '5', '3'], 1.0, 4),
        'baixo': [('1', 2.0), ('5', 2.0)],
        'bateria': None,
        'timbres': ('pulso50', 'pulso12'), 'gate': 1.0, 'eco': (0.5, 0.35), 'vibrato': 0.003, 'repetir': 0.6,
    },
    'heroico': {
        'bpm': 140, 'arpejo': (['1', '5', '3', '5'], 0.5, 4),
        'baixo': [('1', 0.5), ('1', 0.5), ('5', 0.5), ('5', 0.5)] * 2,
        'bateria': {'bumbo': 'x.....x.x.......', 'caixa': '....x.......x...', 'chimbal': 'x.x.x.x.x.x.x.x.'},
        'timbres': ('pulso50', 'pulso25'), 'gate': 0.85, 'eco': None, 'vibrato': 0.0, 'repetir': 0.6,
    },
    'aquatico': {
        'bpm': 100, 'arpejo': (['1', '5', "1'", "3'"], 0.5, 4),
        'baixo': [('1', 1.0), ('5', 1.0), ("1'", 1.0), ('5', 1.0)],
        'bateria': {'bumbo': 'x.......x.......', 'caixa': '................', 'chimbal': '..x...x...x...x.'},
        'timbres': ('pulso25', 'pulso12'), 'gate': 1.0, 'eco': (0.5, 0.3), 'vibrato': 0.006, 'repetir': 0.5,
    },
}

GOLPES = {'bumbo': 36, 'caixa': 38, 'chimbal': 42}

def nova_parte(nome):
    p = stream.Part()
    p.partName = nome
    inst = instrument.Instrument()
    inst.partName = nome
    p.insert(0, inst)
    return p

def compor(subestilo, tom='A', repeticoes=2):
    cfg = SUBESTILOS[subestilo]
    graus = gerar('PECA', HARMONIA[subestilo])
    progressao = [grau_para_acorde(g, tom) for g in graus] * repeticoes

    melodia, harmonia, baixo = nova_parte('Melodia'), nova_parte('Harmonia'), nova_parte('Baixo')
    melodia.insert(0, meter.TimeSignature('4/4'))
    melodia.insert(0, tempo.MetronomeMark(number=cfg['bpm']))
    partes = [melodia, harmonia, baixo]
    bateria = None
    if cfg['bateria']:
        bateria = nova_parte('Bateria')
        partes.append(bateria)

    memoria = {}
    for acorde in progressao:
        if acorde in memoria and random.random() < cfg['repetir']:
            terminais = memoria[acorde]
        else:
            terminais = gerar('MELODIA', MELODIA[subestilo])
            memoria[acorde] = terminais
        for grau, dur in zip(terminais[0::2], terminais[1::2]):
            dur = float(dur)
            if grau == 'R':
                melodia.append(note.Rest(quarterLength=dur))
            else:
                melodia.append(note.Note(nota(grau, acorde, 5), quarterLength=dur))

        ciclo, dur_arp, oitava_arp = cfg['arpejo']
        for i in range(int(4 / dur_arp)):
            harmonia.append(note.Note(nota(ciclo[i % len(ciclo)], acorde, oitava_arp), quarterLength=dur_arp))

        for grau, dur in cfg['baixo']:
            baixo.append(note.Note(nota(grau, acorde, 2), quarterLength=dur))

        if bateria is not None:
            for passo in range(16):
                golpes = [GOLPES[k] for k, padrao in cfg['bateria'].items() if padrao[passo] == 'x']
                if golpes:
                    bateria.append(chord.Chord([note.Note(midi=g) for g in golpes], quarterLength=0.25))
                else:
                    bateria.append(note.Rest(quarterLength=0.25))

    return stream.Score(partes), progressao


SR = 44100
VOLUMES = {'Melodia': 0.30, 'Harmonia': 0.13, 'Baixo': 0.40}

def onda(tipo, freq, n, vibrato=0.0):
    t = np.arange(n) / SR
    f = freq * (1 + vibrato * np.sin(2 * np.pi * 5.5 * t))
    fase = np.cumsum(f) / SR % 1.0
    if tipo.startswith('pulso'):
        duty = {'pulso12': 0.125, 'pulso25': 0.25, 'pulso50': 0.5}[tipo]
        return np.where(fase < duty, 1.0, -1.0)
    if tipo == 'triangulo':
        return np.round((4 * np.abs(fase - 0.5) - 1) * 7.5) / 7.5 
    raise ValueError(tipo)

def envelope(n, ataque=0.002, soltura=0.01):
    env = np.ones(n)
    a, r = min(n, int(ataque * SR)), min(n, int(soltura * SR))
    if a: env[:a] = np.linspace(0, 1, a)
    if r: env[-r:] *= np.linspace(1, 0, r)
    return env

def tambor(midi_num):
    if midi_num == 36:                                   
        n = int(0.12 * SR)
        fase = np.cumsum(np.linspace(150, 50, n) / SR) % 1.0
        return 0.6 * (4 * np.abs(fase - 0.5) - 1) * np.linspace(1, 0, n)
    dur, vol = (0.12, 0.35) if midi_num == 38 else (0.03, 0.12) 
    n = int(dur * SR)
    return vol * np.random.uniform(-1, 1, n) * np.exp(-np.linspace(0, 5, n))

def renderizar_8bit(partitura, subestilo, caminho):
    cfg = SUBESTILOS[subestilo]
    seg_tempo = 60 / cfg['bpm']
    timbre = {'Melodia': cfg['timbres'][0], 'Harmonia': cfg['timbres'][1], 'Baixo': 'triangulo'}
    mix = np.zeros(int(partitura.highestTime * seg_tempo * SR) + 2 * SR)

    for parte in partitura.parts:
        nome = parte.partName
        for el in parte.flatten().notes:
            ini = int(el.offset * seg_tempo * SR)
            if nome == 'Bateria':
                for p in el.pitches:
                    s = tambor(p.midi)
                    mix[ini:ini + len(s)] += s
                continue
            n = max(1, int(el.quarterLength * seg_tempo * SR * cfg['gate']))
            vib = cfg['vibrato'] if nome == 'Melodia' else 0.0
            for p in el.pitches:
                f = 440 * 2 ** ((p.midi - 69) / 12)
                som = VOLUMES[nome] * onda(timbre[nome], f, n, vib) * envelope(n)
                mix[ini:ini + n] += som
                if nome == 'Melodia' and cfg['eco']:
                    atraso, vol_eco = cfg['eco']
                    d = ini + int(atraso * seg_tempo * SR)
                    mix[d:d + n] += vol_eco * som

    mix = 0.9 * mix / max(1e-9, np.abs(mix).max())
    with wave.open(caminho, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    return caminho

PROGRAMAS_MIDI = {'Melodia': 80, 'Harmonia': 80, 'Baixo': 38}
CANAL_BATERIA = 9

def exportar_midi(partitura, caminho):
    partitura.write('midi', fp=caminho)
    nomes = [p.partName for p in partitura.parts]
    mid = mido.MidiFile(caminho)
    trilhas = [t for t in mid.tracks if any(m.type == 'note_on' for m in t)]
    for idx, (trilha, nome) in enumerate(zip(trilhas, nomes)):
        canal = CANAL_BATERIA if nome == 'Bateria' else idx
        programa = PROGRAMAS_MIDI.get(nome, 0)
        novas = [m for m in trilha if m.type != 'program_change']
        for m in novas:
            if hasattr(m, 'channel'):
                m.channel = canal
        pos = next((i for i, m in enumerate(novas) if not m.is_meta), len(novas))
        novas.insert(pos, mido.Message('program_change', channel=canal, program=programa, time=0))
        trilha[:] = novas
    mid.save(caminho)
    return caminho


def main():
    os.makedirs('./Audios', exist_ok=True)
    os.makedirs('./Midis', exist_ok=True)

    estilos_validos = list(SUBESTILOS.keys()) + ['todos', '']
    tons_validos = NOTAS

    sub = sys.argv[1] if len(sys.argv) > 1 else SUBESTILO
    tom = sys.argv[2].capitalize() if len(sys.argv) > 2 else TOM

    if sub.lower() not in estilos_validos:
        sys.exit(f'Estilo inválido: {sub!r}. Use um de {estilos_validos}.')

    if tom not in tons_validos:
        sys.exit(f'Tom inválido: {tom!r}. Use um de {tons_validos} ou deixe em branco para gerar aleatoriamente.')

    if sub.lower() == "todos":
        for nome in SUBESTILOS:
            p, _ = compor(nome, tom, REPETICOES)
            renderizar_8bit(p, nome, f'./Audios/{nome}_{tom}_8bit.wav')
            exportar_midi(p, f'./Midis/{nome}_{tom}.mid')
        print("Todos os estilos gerados")
    else:
        p, prog = compor(sub, tom, REPETICOES)
        caminho = renderizar_8bit(p, sub, f'./Audios/{sub}_{tom}_8bit.wav')
        exportar_midi(p, f'./Midis/{sub}_{tom}.mid')
        print(f'{sub} em {tom} ({SUBESTILOS[sub]["bpm"]} BPM):', ' '.join(prog))
        print('WAV salvo em', caminho)

if __name__ == "__main__":
    main()