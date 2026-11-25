# Relatório: Passada 1 e outliers (rascunho, Adrian)

## Passada 1: K-Means com k de 2 a 10 no Obesity

Na Passada 1 agrupamos as 2.111 pessoas do dataset Obesity com o K-Means, usando apenas as oito variáveis numéricas (`Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF` e `TUE`) e sem olhar a classe real (`NObeyesdad`). As variáveis categóricas ficaram de fora porque o K-Means usa distância euclidiana, que só faz sentido para números. Como as escalas são muito diferentes (idade em anos, altura em metros, peso em quilos), padronizamos tudo com z-score, de modo que cada variável tenha média zero e desvio padrão um e nenhuma domine o cálculo das distâncias. O código está em `notebooks/parte_comum/kmeans_passada1.ipynb`, e a lógica fica em funções de `src/parte_comum/`, que têm testes automáticos.

Para escolher o número de grupos, rodamos o K-Means com k de 2 a 10 e desenhamos o Método do Cotovelo. A inércia cai de forma gradual, de cerca de 14.368 com k = 2 para cerca de 8.057 com k = 10, e não aparece um joelho nítido que indique um k único. Conferimos também o coeficiente de silhueta, que ficou praticamente plano entre 0,145 e 0,179 para todos os valores de k. Ou seja, os dados não apontam um número de grupos claramente melhor. Por isso adotamos k = 7, o número de classes reais de `NObeyesdad`, o que também permite comparar os grupos com as classes. Uma consequência é que, com o mesmo k e a mesma semente aleatória (42), o resultado da Passada 1 coincide com o da Passada 2, que usa k fixo: 38,8% de acurácia nos dois casos.

Para visualizar os grupos usamos o PCA, que reduz as oito variáveis a duas componentes principais. As duas componentes explicam 41,3% da variância (22,6% e 18,7%), então o gráfico mostra só uma parte da informação, e os grupos aparecem bastante sobrepostos. O PCA serve apenas para desenhar: o K-Means continuou usando as oito variáveis padronizadas.

Como o K-Means é não supervisionado, ele não conhece os nomes das classes. Depois de formar os grupos, rotulamos cada um com a classe real que mais aparece dentro dele (em caso de empate, vale a ordem alfabética, para o resultado ser reproduzível). Com k = 7, os grupos ficaram com 253 a 367 pessoas e receberam seis classes diferentes: `Obesity_Type_III` ficou com dois grupos e `Overweight_Level_II` não foi a classe majoritária de nenhum, então nunca é prevista e seu recall é zero. A acurácia foi de aproximadamente 38,8%, a precisão média (macro) de 31,0% e o recall médio (macro) de 38,4%. Por classe, o recall foi de 100% em `Obesity_Type_III` (as 324 pessoas dessa classe caíram em grupos rotulados com ela), 46% em `Insufficient_Weight`, 42% em `Obesity_Type_II`, 36% em `Normal_Weight`, 23% em `Obesity_Type_I`, 22% em `Overweight_Level_I` e 0% em `Overweight_Level_II`.

Esses resultados mostram que o K-Means formou grupos, mas que eles coincidem só em parte com as classes de obesidade. Segundo a descrição do dataset, as classes são definidas a partir do IMC, isto é, de peso e altura, enquanto o K-Means dá o mesmo peso às oito variáveis, inclusive hábitos alimentares e de atividade física, que provavelmente não separam bem as classes. Isso ajuda a explicar por que a classe mais extrema (`Obesity_Type_III`) é a única bem separada e por que as classes vizinhas de sobrepeso e obesidade leve se misturam.

## Outliers do BankChurners

Para avaliar os valores extremos do BankChurners (já com os Unknown tratados) usamos os mesmos critérios da Parte Comum: o IQR, que marca valores abaixo de Q1 − 1,5·IQR ou acima de Q3 + 1,5·IQR, e o z-score, que marca valores com módulo maior que 3. O código está em `src/parte_especifica/eda_outliers.ipynb`, com a lógica em `src/parte_especifica/outliers.py` (testada), e a página Outliers do dashboard usa as mesmas funções.

Pelo IQR, 10 das 14 variáveis numéricas têm outliers, de 0,02% (`Customer_Age` e `Total_Trans_Ct`) a 9,7% (`Credit_Limit`, com 984 clientes). No total, 3.326 clientes (32,8% da base) têm pelo menos um outlier. O z-score é mais rigoroso em variáveis assimétricas: `Credit_Limit` tem 984 outliers pelo IQR e nenhum pelo z-score. Todos os valores extremos são plausíveis: limite de crédito de até US$ 34.516, até US$ 18.484 transacionados em 12 meses, clientes de até 73 anos, até 56 meses de relacionamento e até 139 transações, sem valores negativos ou fora das escalas de contagem. `Credit_Limit` e `Avg_Open_To_Buy` têm correlação de 0,996, então apontam para os mesmos clientes, os de limite alto.

Também comparamos a taxa de cancelamento entre quem é outlier e quem não é. A taxa da base toda é de 16,1%. Quem é outlier em `Total_Ct_Chng_Q4_Q1` cancela mais (22,1% contra 15,8%), e quem é outlier em `Total_Trans_Amt`, os grandes gastadores, cancela bem menos (9,8% contra 16,7%). Ou seja, os outliers carregam informação sobre o cancelamento. Por isso propomos manter todos os valores e não remover linhas: remover os outliers de todas as variáveis descartaria 32,8% da base (restariam 6.801 dos 10.127 clientes), justamente os perfis mais distintos. Como recurso de análise, limitar os valores nas cercas do IQR reduz a assimetria de `Credit_Limit` de 1,67 para 1,20 e a de `Total_Trans_Amt` de 2,04 para 0,84, sem perder nenhum cliente. As variáveis de contagem (`Contacts_Count_12_mon`, `Months_Inactive_12_mon`, `Months_on_book`, `Customer_Age` e `Total_Trans_Ct`) são tratadas como valores válidos da escala, sem ajuste.

<!--
NOTAS PARA REVISÃO DO GRUPO (apagar antes de montar o relatorio.pdf)
- Os números acima foram recalculados dos dados e dos notebooks (kmeans_passada1.ipynb e eda_outliers.ipynb).
- Decisão a confirmar: k = 7 na Passada 1. O cotovelo e a silhueta não apontam um k melhor, então a Passada 1 deu o
  mesmo resultado da Passada 2. Se o grupo preferir outro k, é só mudar a constante K no notebook e na seção acima.
- A decisão de manter os outliers (e não removê-los) é uma proposta; o grupo precisa concordar.
- Conferir na descrição do dataset no UCI (544) a frase de que as classes são definidas a partir do IMC.
- Texto escrito com apoio de IA (Claude Code): declarar na seção de uso de IA do relatório.
-->
