# Relatório: textos finais (Fernando)

## Pergunta de pesquisa

Quais características do comportamento dos clientes estão mais associadas ao cancelamento do cartão de crédito e podem ajudar o banco a identificar clientes com maior risco de cancelamento?

## Público-alvo

O dashboard é destinado às equipes de análise de dados, marketing e relacionamento com clientes do banco. A linguagem é objetiva e utiliza gráficos e indicadores para facilitar a identificação de padrões de comportamento, ajudando a compreender o cancelamento e a pensar em estratégias para retenção de clientes.

## Classificação das variáveis

Adotamos a classificação das variáveis apresentada no dicionário do dataset, considerando seus significados e seus tipos estatísticos.

## Mecanismo de ausência

Para Education_Level, o mecanismo mais próximo parece ser MCAR, pois as taxas de Unknown apresentam poucas diferenças entre os grupos analisados. Para Marital_Status, existem algumas diferenças conforme outras variáveis, então podemos considerar a possibilidade de MAR. Já em Income_Category, a ausência apresenta uma diferença muito grande entre homens e mulheres, indicando um comportamento mais próximo de MAR. Não é possível afirmar esses mecanismos com certeza apenas pelas tabelas, principalmente porque não conseguimos observar diretamente o motivo pelo qual cada cliente deixou de informar seus dados.

## Justificativa do tratamento

Decidimos manter Unknown como uma categoria própria porque não sabemos qual seria o valor correto de cada informação ausente. Substituir pela moda poderia criar informações que não correspondem à realidade dos clientes. Além disso, manter essa categoria permite analisar os registros sem excluir clientes ou perder informações importantes.

## Passada 2: escolha das variáveis e matriz de confusão

Utilizamos somente as oito variáveis numéricas porque o K-Means trabalha com cálculos de distância, então precisa de valores numéricos para formar os grupos. As variáveis categóricas continuaram sendo analisadas na EDA, mas não entraram no agrupamento. Height e Weight foram mantidas porque representam características físicas importantes para diferenciar os perfis relacionados ao peso. Na matriz de correlação, a relação entre altura e peso é positiva, com correlação de aproximadamente 0,46, indicando uma associação moderada entre essas variáveis.

## Storytelling

A exploração mostrou que existem diferenças no comportamento dos clientes que permaneceram no banco e daqueles que cancelaram o cartão. Os gráficos foram construídos para destacar essas diferenças de forma visual e facilitar a interpretação pelo público-alvo. Utilizamos o vermelho para chamar atenção para os grupos com maior risco de cancelamento, a linha da média como referência para comparação e títulos que apresentam diretamente a principal mensagem de cada gráfico. Dessa forma, o dashboard não mostra apenas números, mas também ajuda o usuário a entender o que esses resultados significam.

## Resposta à pergunta de pesquisa

Com base nas duas visualizações explanatórias, percebemos que o cancelamento está relacionado tanto ao comportamento de utilização do cartão quanto à quantidade de produtos contratados pelo cliente.

Na primeira visualização, observamos que os clientes que tiveram uma queda forte no uso do cartão durante o quarto trimestre apresentaram taxas de cancelamento muito altas, principalmente aqueles com menos de 60 transações. Já os clientes com 60 ou mais transações apresentaram taxas abaixo de 6,5%, independentemente do ritmo de utilização.

Na segunda visualização, percebemos que clientes com apenas 1 ou 2 produtos contratados apresentam uma taxa de cancelamento de 26,9%, enquanto aqueles com 4 a 6 produtos apresentam uma taxa de 11,4%. Além disso, os clientes com 1 ou 2 produtos representam 21,3% da base, mas correspondem a 35,6% dos cancelamentos.

Portanto, concluímos que a baixa utilização do cartão, principalmente quando acompanhada de uma queda no uso, e a contratação de poucos produtos são características importantes para identificar clientes com maior risco de cancelamento. Essas informações podem ajudar o banco a direcionar ações de relacionamento e retenção para os grupos que precisam de mais atenção.
