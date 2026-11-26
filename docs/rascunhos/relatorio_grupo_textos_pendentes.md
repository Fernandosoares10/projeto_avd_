# Textos que o grupo ainda precisa escrever

Escreva cada texto logo abaixo do título `##` correspondente, com as palavras do grupo. Depois rode
`python docs/montar_relatorio.py` na raiz do projeto. Seção vazia aparece como PENDENTE (em amarelo) no PDF.
Este bloco de orientação (antes do primeiro `##`) não entra no relatório.

Perguntas de apoio (o que o enunciado pede em cada parte):

- Relações (Parte Comum): figuras `out/parte_comum/eda_relacional_correlacao_comum.png` e
  `eda_relacional_peso_altura_classe.png`. Quais variáveis se relacionam mais forte? Como peso e altura se
  distribuem entre as classes? Isso se conecta com o resultado do K-Means?
- Passada 1 e Passada 2: Tabelas de matriz de confusão e de precisão/recall no relatório. Quais classes cada
  passada separa bem e quais confunde? Por que algumas ficam com 0%? A matriz da Passada 1 é retangular: por quê?
  Silhueta: 0,169 (k = 5) e 0,166 (k = 7), calculada nos notebooks do K-Means.
- Exploratória 3 e explanatória 1: uma ou duas frases dizendo por que esse tipo de gráfico foi escolhido
  (o enunciado pede "por que aquele tipo de visualização foi escolhido" em toda nota analítica).

## Relações entre as variáveis (Parte Comum)
Na matriz de correlação da Parte Comum, o par com associação mais forte é peso (Weight) e altura (Height) (r = 0,46), enquanto variáveis de hábitos cotidianos como número de refeições principais (NCP) e tempo em dispositivos eletrônicos (TUE) quase não se relacionam com as demais. No gráfico de dispersão de peso × altura por classe, os extremos (Insufficient_Weight e Obesity_Type_III) ficam mais isolados nas pontas, mas as faixas intermediárias (Normal_Weight, Overweight_Level_I, Overweight_Level_II e Obesity_Type_I) se sobrepõem ao longo das fronteiras contínuas de IMC. Esse padrão ajuda a explicar o comportamento do K-Means, que consegue isolar melhor Obesity_Type_III, mas confunde as classes vizinhas de sobrepeso e obesidade leve.

## Interpretação da matriz e das métricas (Passada 1)

## Interpretação das métricas (Passada 2)

## Por que este gráfico (exploratória 3)
Escolhemos o heatmap porque ele cruza duas variáveis discretas de contagem (Contacts_Count_12_mon e Months_Inactive_12_mon, ambas de 0 a 6) e mostra, em uma única grade, a taxa de cancelamento (%) e o tamanho amostral (n) em cada combinação. Gráficos de barras ou de dispersão não permitiriam comparar todas as 49 combinações de forma legível, pois gerariam excesso de barras ou sobreposição total de pontos nos mesmos valores inteiros.

## Por que este gráfico (explanatória 1)
As barras agrupadas permitem comparar a taxa de cancelamento entre clientes com queda forte no 4º trimestre (Q4/Q1 < 0,60) e clientes com uso estável ou crescente (Q4/Q1 ≥ 0,60) dentro de cada faixa de volume anual de transações (Total_Trans_Ct) e entre as faixas ao mesmo tempo. A cor vermelha destaca imediatamente a zona de maior risco — concentrada abaixo de 60 transações por ano — para a equipe de gestão e retenção de clientes.