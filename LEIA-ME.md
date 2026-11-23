# Saída da Caverna — resposta melódica

Execute:

```bash
python3 saida_contracanto.py
```

O script preserva uma referência sem a segunda voz e gera a versão com
contracanto. A resposta de violoncelo é `Mi3–Dó3 / Si2–Sol2`, tem quatro notas,
usa o canal MIDI 2 (índice técnico 1), fica 12 pontos de velocity abaixo da
melodia e aparece somente nos compassos 5–6.

Arquivos gerados:

- `saida_sem_resposta.mid` e `saida_sem_resposta.wav`
- `saida_contracanto.mid` e `saida_contracanto.wav`

A renderização usa `/usr/share/sounds/sf2/TimGM6mb.sf2`. Para usar a mesma
SoundFont em outro computador, ajuste apenas a constante `SOUNDFONT` no início
do script.
