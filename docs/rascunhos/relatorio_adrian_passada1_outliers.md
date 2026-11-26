# Relatório: Passada 1, discussão crítica e outliers

## Passada 1: escolha do k e resultados

Na Passada 1, o K-Means foi testado com valores de k entre 2 e 10, utilizando o Método do Cotovelo. A inércia diminuiu conforme aumentava o número de grupos, mas a curva não apresentou um cotovelo muito claro. Pelo critério da maior distância até a reta, o valor escolhido foi k = 5, embora k = 6 tenha ficado próximo. Com cinco grupos, algumas classes reais ficaram misturadas e duas delas (Obesity_Type_II e Overweight_Level_II) não apareceram como classe majoritária em nenhum cluster. A acurácia foi de 33,4%, mostrando que os grupos encontrados representam apenas parcialmente as classes originais.

## Discussão crítica: qual passada gerou grupos mais coerentes?

Comparando os resultados, a Passada 2, com k = 7, apresentou um desempenho melhor que a Passada 1. Ela alcançou 38,8% de acurácia, contra 33,4% da Passada 1, e conseguiu representar seis das sete classes, enquanto a Passada 1 deixou duas classes sem representação. Outro ponto é que a Passada 2 alcançou 100% de recall para Obesity_Type_III, mostrando que identificou todos os registros dessa classe. Portanto, considerando as métricas e a representação das classes, a Passada 2 gerou grupos mais coerentes com as categorias originais. Mesmo assim, os resultados mostram que ainda existe bastante mistura entre os grupos, então nenhum dos dois métodos conseguiu separar perfeitamente as classes.

## Granularidade das classes

As sete classes fazem sentido porque permitem identificar diferentes níveis de condição nutricional, mantendo um detalhamento maior. Porém, os dados mostram que algumas categorias são muito parecidas entre si. Isso acontece principalmente com Overweight_Level_I, Overweight_Level_II e Obesity_Type_I, que apresentam bastante sobreposição nos seus perfis. Por isso, uma possibilidade seria juntar Overweight_Level_I e Overweight_Level_II em uma única categoria chamada Sobrepeso. Essa mudança poderia facilitar a separação dos grupos, mas também faria perder parte do detalhamento. Assim, manter as sete classes é interessante para preservar as diferenças entre os níveis, enquanto trabalhar com quatro macro-classes pode ser mais adequado para uma análise com grupos mais amplos. Não existe uma única escolha correta: depende do objetivo da análise.

## Outliers do BankChurners

### Os outliers são erros ou clientes reais?

Os outliers parecem ser clientes reais, e não erros nos dados. Isso porque os valores extremos continuam dentro de limites possíveis, sem números negativos ou fora das escalas esperadas. Por exemplo, existem clientes com limite de crédito de até US$ 34.516, movimentação de até US$ 18.484 e até 139 transações em 12 meses. Pelo critério IQR, foram encontrados outliers em 10 das 14 variáveis numéricas, e 3.326 clientes (32,8% da base) possuem pelo menos um valor extremo. Portanto, ser outlier não significa que o dado esteja errado, mas sim que aquele cliente tem um comportamento diferente da maioria.

### Ser outlier tem relação com cancelar?

A tabela mostra que existe relação em algumas variáveis, mas não significa que todo outlier tenha maior chance de cancelar. Por exemplo, os clientes considerados outliers em Total_Ct_Chng_Q4_Q1 apresentam taxa de cancelamento de 22,1%, enquanto os demais têm 15,8%. Já em Total_Trans_Amt, acontece o contrário: os outliers cancelam menos, com taxa de 9,8%, contra 16,7% dos demais. Em Credit_Limit, as taxas são iguais, de 16,1%. Isso mostra que os valores extremos podem representar comportamentos diferentes e que alguns deles ajudam a entender o cancelamento.

### Tratamento adotado

O grupo propõe manter os outliers e não remover os clientes, pois os valores são plausíveis e podem trazer informações importantes para a análise. Remover todos os clientes que possuem pelo menos um outlier faria a base cair de 10.127 para 6.801 clientes, ou seja, seriam perdidos 32,8% dos dados. Como alternativa, podemos limitar alguns valores nas cercas do IQR para diminuir a assimetria das variáveis, sem excluir nenhum cliente. Assim, a decisão principal é manter os registros e evitar a perda de informações importantes.
