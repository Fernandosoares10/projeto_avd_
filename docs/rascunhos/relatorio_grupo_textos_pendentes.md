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
Na matriz de correlação da Parte Comum, o par com associação mais forte é peso (Weight) e altura (Height) (r = 0,46), seguido pela correlação negativa entre idade (Age) e tempo em dispositivos eletrônicos (TUE) (r = -0,30), enquanto a maioria das variáveis de hábitos (como FCVC, NCP e CH2O) apresenta correlações fracas entre si. No gráfico de dispersão de peso × altura por classe, os extremos (Insufficient_Weight e Obesity_Type_III) ficam mais isolados nas pontas, mas as faixas intermediárias (Normal_Weight, Overweight_Level_I, Overweight_Level_II e Obesity_Type_I) se sobrepõem ao longo das fronteiras contínuas de IMC. Esse padrão ajuda a explicar o comportamento do K-Means, que consegue isolar melhor Obesity_Type_III, mas confunde as classes vizinhas de sobrepeso e obesidade leve.

## Interpretação da matriz e das métricas (Passada 1)
A matriz da Passada 1 tem sete linhas e cinco colunas porque cada linha é uma classe real e cada coluna é um dos cinco clusters do K-Means. Com menos clusters do que classes, pelo menos duas classes ficariam sem cluster. Isso aconteceu com Overweight_Level_II e Obesity_Type_II, que não foram maioria em nenhum grupo e por isso ficaram com 0% de precisão e recall. A maior parte de Obesity_Type_II (208 de 297) caiu no cluster 1, junto com Obesity_Type_III, e Overweight_Level_II se espalhou pelos cinco clusters.

Obesity_Type_III foi a classe mais bem identificada, com recall de 91,4%. A precisão foi de 47,9% porque cerca de um terço do cluster 1 é de Obesity_Type_II. As demais classes tiveram valores baixos. Insufficient_Weight e Normal_Weight chegaram a 48,2% e 42,9% de recall, mas com precisão de 31,5% e 25,6%, já que os clusters 2 e 3 misturam pessoas de quase todas as classes. Overweight_Level_I e Obesity_Type_I ficaram entre 22% e 30% nas duas métricas. Os clusters 2, 3 e 4 têm peso médio parecido, perto de 70 kg, e se diferenciam mais por hábitos como atividade física (FAF) e número de refeições (NCP). Como as classes vêm do IMC e o K-Means trata as oito variáveis com o mesmo peso, os grupos do meio não acompanharam o peso das pessoas. A silhueta de 0,169 mostra clusters bem sobrepostos, o que combina com a acurácia de 33,4%.
## Interpretação das métricas (Passada 2)
Na Passada 2, Obesity_Type_III teve recall de 100%, com todas as 324 pessoas da classe em clusters mapeados para ela. A precisão ficou em 63,0% porque dois clusters (2 e 4) foram mapeados para Obesity_Type_III e receberam também 89 pessoas de Obesity_Type_II. Obesity_Type_II, que tinha 0% na Passada 1, ganhou o cluster 5 e chegou a 42,4% de recall e 37,7% de precisão, mas esse cluster ainda tem 95 pessoas de Obesity_Type_I e 63 de Overweight_Level_II.

Overweight_Level_II continuou com 0%. Como Obesity_Type_III ficou com dois clusters, sobraram cinco para as outras seis classes, e Overweight_Level_II não foi maioria em nenhum. As classes do meio também continuaram fracas. Overweight_Level_I teve cerca de 22% de recall e de precisão, com suas pessoas divididas quase igualmente entre os clusters de Insufficient_Weight, Normal_Weight e Overweight_Level_I. Obesity_Type_I teve 22,5% de recall, e mais pessoas dessa classe foram para o cluster de Obesity_Type_II (95) do que para o seu (79). Insufficient_Weight (46,0% de recall) e Normal_Weight (35,5%) se confundiram bastante entre si. A acurácia subiu de 33,4% para 38,8%, mas a silhueta quase não mudou (0,166 contra 0,169). A melhora veio principalmente de Obesity_Type_II ter ganhado um cluster e de Obesity_Type_III ter sido toda identificada. Os grupos em si não ficaram mais separados.
## Por que este gráfico (exploratória 3)
Escolhemos o heatmap porque ele cruza duas variáveis discretas de contagem (Contacts_Count_12_mon e Months_Inactive_12_mon, ambas de 0 a 6) e mostra, em uma única grade, a taxa de cancelamento (%) e o tamanho amostral (n) em cada combinação. Gráficos de barras ou de dispersão não permitiriam comparar todas as 49 combinações de forma legível, pois gerariam excesso de barras ou sobreposição total de pontos nos mesmos valores inteiros.

## Por que este gráfico (explanatória 1)

As barras agrupadas permitem comparar, lado a lado, a taxa de cancelamento entre clientes com queda forte no 4º trimestre (Q4/Q1 < 0,60) e clientes com uso estável ou crescente (Q4/Q1 ≥ 0,60) dentro de cada faixa de transações anuais (Total_Trans_Ct) e entre as faixas ao mesmo tempo. A cor vermelha destaca visualmente os grupos de maior risco em relação à média geral de 16,1% (especialmente abaixo de 60 transações), facilitando a priorização de ações de retenção pelas equipes de análise de dados, marketing e relacionamento do banco.

## Dashboard (visão geral)

O dashboard é aberto com `streamlit run src/parte_especifica/dashboard.py`, a partir da raiz do projeto. As páginas seguem a ordem da análise: primeiro a qualidade dos dados, depois as distribuições, as relações entre as variáveis e os outliers, e por fim uma página dedicada à Parte Comum.

- **Início**: apresentação do projeto e botão para baixar o relatório completo em PDF.
- **Qualidade dos dados**: estrutura do dataset, valores Unknown e tratamento adotado, e a visualização exploratória 1; permite escolher a variável de agrupamento e mostrar ou esconder os valores discrepantes.
- **Distribuições**: filtros na barra lateral (situação do cliente, gênero, idade, faixa de renda, categoria do cartão, escolaridade e estado civil) que valem para todos os gráficos da página, escolha da variável, opção de separar por situação do cliente, download do recorte em CSV e a visualização exploratória 2.
- **Relações**: filtro por categoria do cartão, escolha entre correlação de Pearson e de Spearman, comparação lado a lado de dois perfis de clientes, gráfico de dispersão com escolha dos eixos X e Y e da variável de cor, a visualização exploratória 3 e as duas visualizações explanatórias.
- **Outliers**: ajuste do multiplicador das cercas do IQR, comparação entre os dados originais e tratados, taxa de cancelamento entre outliers e demais clientes, download dos clientes selecionados e a visualização exploratória 4.
- **Parte Comum**: K-Means do dataset Obesity com escolha do número de grupos e animação da transição entre a Passada 1 (k livre) e a Passada 2 (k fixo).
