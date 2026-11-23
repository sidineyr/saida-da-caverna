# Saída da Caverna

Composição musical curta criada em Python com **music21** e renderizada com **FluidSynth**. Esta versão acrescenta uma resposta melódica discreta de violoncelo nos compassos 5–6, criando um diálogo entre duas vozes sem competir com a melodia principal.

## Resultado musical

- Duração: **24,32 segundos**
- Resposta: **Mi3–Dó3 / Si2–Sol2**
- Instrumento: **violoncelo**
- Entrada: somente nos compassos **5–6**
- Quantidade: **quatro notas**
- Dinâmica: **12 pontos de velocity abaixo da melodia**
- Canais MIDI: melodia 1, violoncelo 2 e harmonia 3

## Arquivos

| Arquivo | Descrição |
| --- | --- |
| `saida_contracanto.py` | Código-fonte e validações |
| `saida_contracanto.mid` | Versão MIDI com resposta |
| `saida_contracanto.wav` | Áudio renderizado com resposta |
| `saida_sem_resposta.mid` | Referência MIDI sem resposta |
| `saida_sem_resposta.wav` | Referência em áudio sem resposta |
| `requirements.txt` | Dependências Python |
| `Saida_da_Caverna_contracanto.zip` | Pacote completo |

## Executar

Requer Python 3 e FluidSynth instalado no sistema.

```bash
python -m pip install -r requirements.txt
python saida_contracanto.py
```

A renderização usa a SoundFont `TimGM6mb.sf2`. Caso ela esteja em outro local, altere a constante `SOUNDFONT` no início do script.

## Critérios validados

O script verifica automaticamente:

- quatro notas na voz de resposta;
- presença exclusiva nos compassos 5–6;
- notas pertencentes aos acordes do trecho;
- canal MIDI exclusivo;
- velocity abaixo da melodia;
- WAV audível;
- duração inferior a 30 segundos.

## Licenças

- **Código Python:** MIT — consulte [LICENSE](LICENSE).
- **Composição, MIDI, WAV e documentação:** CC BY 4.0 — consulte [LICENSE-CONTENT.md](LICENSE-CONTENT.md).

## Autor

**Sidiney Rodrigues**  
Pedagogo, educador e desenvolvedor de projetos educacionais abertos.

- [Portfólio](https://sidineyr.github.io/)
- [GitHub](https://github.com/sidineyr)
