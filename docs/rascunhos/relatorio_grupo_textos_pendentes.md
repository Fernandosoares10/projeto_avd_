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

## Dashboard (visão geral)

O dashboard é aberto com `streamlit run src/parte_especifica/dashboard.py`, a partir da raiz do projeto. As páginas seguem a ordem da análise: primeiro a qualidade dos dados, depois as distribuições, as relações entre as variáveis e os outliers, e por fim uma página dedicada à Parte Comum.

- **Início**: apresentação do projeto e botão para baixar o relatório completo em PDF.
- **Qualidade dos dados**: estrutura do dataset, valores Unknown e tratamento adotado, e a visualização exploratória 1; permite escolher a variável de agrupamento e mostrar ou esconder os valores discrepantes.
- **Distribuições**: filtros na barra lateral (situação do cliente, gênero, idade, faixa de renda, categoria do cartão, escolaridade e estado civil) que valem para todos os gráficos da página, escolha da variável, opção de separar por situação do cliente, download do recorte em CSV e a visualização exploratória 2.
- **Relações**: filtro por categoria do cartão, escolha entre correlação de Pearson e de Spearman, comparação lado a lado de dois perfis de clientes, gráfico de dispersão com escolha dos eixos X e Y e da variável de cor, a visualização exploratória 3 e as duas visualizações explanatórias.
- **Outliers**: ajuste do multiplicador das cercas do IQR, comparação entre os dados originais e tratados, taxa de cancelamento entre outliers e demais clientes, download dos clientes selecionados e a visualização exploratória 4.
- **Parte Comum**: K-Means do dataset Obesity com escolha do número de grupos e animação da transição entre a Passada 1 (k livre) e a Passada 2 (k fixo).
