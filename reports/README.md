# Relatórios Automáticos de Tempo (LLM Red-Teaming)

Esta pasta contém relatórios gerados automaticamente pelo GitHub Actions, com base nas *issues* do projeto.

## Objetivo

O sistema recolhe semanalmente as *issues* fechadas e calcula o tempo estimado e real gasto por cada colaborador, usando as anotações colocadas no corpo das *issues*.

> É **importante selecionar os assignees** de cada *issue* além de escrever os `@username` nas secções de tempo. Além disso certifiquem-se que no perfil do GitHub têm o vosso nome real porque é o que vai aparecer no csv. Assim o workflow consegue mapear corretamente cada tempo ao colaborador.

### Exemplo de formatação das *issues*

No corpo da *issue*, devem constar os tempos de cada utilizador:
Estimated Time (minutes)\
@username1 60 @username2 32

Actual Time (minutes)\
@username1 120 @username2 33


---

## Relatórios Gerados

### Relatório Semanal
- Ficheiro: `reports/YYYY_MM_DD_weekly_report.csv`
- Contém apenas as *issues* **fechadas desde a última segunda-feira**.
- Colunas:
  - **Nome (real)** do utilizador
  - **Tempo estimado (min)**
  - **Tempo real (min)**

### Relatório Total
- Ficheiro: `reports/total_time_report.csv`
- Contém o total acumulado de **todo o histórico de *issues***.
- Colunas:
  - **Nome (real)** do utilizador
  - **Tempo total estimado (min)**
  - **Tempo total real (min)**

---

## Funcionamento do Workflow

- O *workflow* `Generate Weekly Time Report` é executado automaticamente **todas as segundas-feiras às 16:00 (hora de Portugal)**.
- Também pode ser executado manualmente através da aba **Actions → Generate Weekly Time Report → Run workflow**.
- Os ficheiros gerados são automaticamente **adicionados e enviados para o repositório**.

---
