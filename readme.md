# Gerador de Trilhas Metroidvania 8-bit

Programa que gera trilhas sonoras no estilo Metroidvania 8-bit usando
Gramáticas Generativas. Cada execução produz um áudio distinto, com
progressão harmônica, melodia, baixo e bateria sorteados
probabilisticamente.

## Instalação

Requer Python 3 e as dependências:

```bash
pip install numpy mido music21
```

## Uso

Para gerar um audio aleatório é necessário somente digitar
``` bash
 python3 gerador.py
```
Mas também é possível escolher o subestilo e a tonalidade
``` bash
python3 gerador.py castelo Db # estilo Castelo em Ré bemol
python3 gerador.py todos      # gera todos os 6 subestilos
```
os arquivos são salvos nas pastas
 - `./Audios/` -- trilhas em WAV
 - `./Midis/ ` -- partituras em MIDI
### Resumo do progama

O programa consiste em um gerador de audio no estilo metroidvania simulando 8 bit.
Os áudios são gerados usando algoritmos generativos, que por meio de probabilidade, geram cadeias aleatórias formando os áudios.

#### Temas
O programa é capaz de gerar audios em 6 categorias diferentes, inspiradas em jogos do estilo 8 bits com seus respectivos temas:
- Castelo
- Caverna
- Chefe
- Santuario
- Heroico
- Aquatico

Sendo que esses temas são gerados aleatóriamente também, mas podem ser definidas dentro do programa.

## Uso de IA
Foram utilizadas ferramentas de IA durante o desenvolvimento do
programa, especificamente para:

- Adaptação das cadeias gramaticais ao estilo Metroidvania;
- Implementação do sintetizador 8-bit;
- Auxílio na criação de algumas categorias.

O uso foi restrito a esses pontos, além de revisão de código e texto.

[Link Conversa de Revisão](https://chat.deepseek.com/share/lfslhfqqvyf3glvleb)

[link de conversa ajuda código e inspiração](https://chat.deepseek.com/share/y1c47jpzuoqplyd5yk)
