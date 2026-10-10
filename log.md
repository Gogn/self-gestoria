# Журнал базы знаний

Хронология операций с публичной базой (`knowledge/`, `sources/`, `templates/`,
`examples/`, skills). Личное — в `my-data/log.md`. Только дописывается в конец.

Заголовок записи строгий — по нему работают `grep` и lint:

```
## [ГГГГ-ММ-ДД] <операция> | <что>
```

| Операция | Когда |
|---|---|
| `ingest` | новый источник внесён в базу (`/ingest`) |
| `verify` | существующее утверждение сверено с первоисточником |
| `lint` | прогон `/lint-knowledge`, по которому что-то исправлено |
| `query` | вывод из разговора сохранён в базу |

Последние записи: `grep '^## \[' log.md | tail -5`.
До 2026-10-10 журнала не было — история изменений в `git log`.

## [2026-10-10] lint | Первый прогон /lint-knowledge
- skill `lint-knowledge`: скрипт механических проверок + смысловые проверки по SKILL.md
- найдено: `quarterly-filing` считал итог 303 как `46 − 110`, хотя `knowledge/` это
  уже опровергал (исправление `6442013` не дошло до кода skill) → исправлено
- найдено: casilla 05 модели 130 описана в разных файлах по-разному → см. verify ниже

## [2026-10-10] verify | Модель 130: casilla 05 и раздел III (12–19)
- источник: Instrucciones 130 (страница AEAT от 11.09.2026) + подписи граф в форме 2026
- 05 = Σ положительных 07 прошлых кварталов − Σ их 16 (не Σ 19 и не «уплачено»)
- нумерация 13–18 была сдвинута; цепочка 12 → 14 → 17 → 19 переписана
- изменено: `modelo-130-irpf.md`, `quarterly-filing`, `consistency-check`,
  `import-history`, шаблоны, пример; ссылка на Instrucciones в `aeat-sede-navigation.md`
- попутно: переносимый НДС-кредит — casilla 87 последней 303, не 110 и не итог

## [2026-10-10] lint | Проверка сумм из my-data/, механические находки
- `.claude/skills/lint-knowledge/lint.py`: публичные файлы сверяются с суммами из текстовых файлов `my-data/`
- шаблоны и пример переведены на условные суммы
- шапки (год формы, «Перепроверять»), ссылки на файлы без входящих ссылок

## [2026-10-10] verify | ingresos-workflow.md и 5 % gastos de difícil justificación
- источники: LIRPF 14, 28, 30, 32, DA 56ª; RIRPF 7, 26, 30; LIS 11; LIVA 75, 79;
  RD 1619/2012 5, 12; PGC NRV 11ª; Instrucciones 130; страница курсов ЕЦБ
- 🔴 5 % входят в casilla 02 модели 130 в simplificada — база утверждала обратное
  (`gastos-deducibles.md`, `modelo-130-irpf.md`, `modelo-100-renta.md`)
- проверка курса была перевёрнута (в записи ЕЦБ невыгодный курс выше официального) →
  `ingresos-workflow.md` и `CLAUDE.md`
- открыто: дата счёта против периода работ на стыке кварталов; курсовая разница в 130;
  курс для даты в выходной; номер casilla 740 в 036; BOE-идентификатор Ley 46/1998

## [2026-10-10] ingest | Слой sources/ — первые выдержки
- `sources/fetch.py` + `manifest.json`: текст из API BOE и со страниц AEAT, без пересказа
- выдержки в `sources/`: `sources/boe/lirpf.md`, `sources/boe/rirpf.md`, `sources/boe/lis.md`,
  `sources/boe/liva.md`, `sources/boe/rd-1619-2012-facturacion.md`, `sources/boe/pgc-nrv-11.md`,
  `sources/aeat/instrucciones-130.md`
- lint: шапка, хеш текста (ловит ручные правки), сверка с манифестом
- изменено: `sources-primarias.md` (ссылки на выдержки), `modelo-130-irpf.md`,
  `gastos-deducibles.md`, `ingresos-workflow.md`
