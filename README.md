# ANÁLISE MOTOR BAJA UFTM

## Descrição dos módulos

- **chemistry**: definição de moléculas com propriedades térmicas;
- **engine**: cálculo de propriedades térmicas no funcionamento do motor;
- **input_parameters**: leitura de variáveis iniciais definidas no `sample.env`;
- **main**: arquivo principal a ser chamado para obter resultados;
- **stage**: definição de um estágio genérico para ciclos termodinâmicos;
- **utils**: funções genéricas utilizadas no devenvolvimento.

## Modo de usar

- Abra o arquivo `sample.env` e defina os valores de cada variável necessária para o desenvolvimento;
- No arquivo `main.py` defina o resultado desejado, seja o cálculo pontual de valores, ou cálculo de vários pontos para geração de gráficos.