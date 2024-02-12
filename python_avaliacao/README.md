# Avaliação Python

Este é um breve guia para ajudá-lo com o projeto.

## Pré-requisitos

Antes de começar, certifique-se de ter o Python e o pip instalados em sua máquina.

## Instalação

Para instalar as dependências necessárias, execute o seguinte comando no terminal:

```
pip install -r requirements.txt
````

## Rodar o Projeto

Para rodar o projeto execute o seguinte comando no terminal:

```
python app.py
````


## Para conseguir fazer as requisições é necessário realizar login na aplicação

Será retornado um token para forncer no cabeçalho em autorização da chamadas

    POST http://localhost:5000/login

```
    {
        "username":"admin",
        "password":"admin"
    }
```	




## API em Rust - Operações CRUD
Operações CRUD (Create, Read, Update, Delete). Aqui estão os endpoints disponíveis: (obs: ao fornecer o cnpj na url deve passar no apenas numeros, mas para criação de uma empresa não é necessario remover os caracteres, ou seja, pode ser COM ou SEM, existe tratativa.)


### Listar Todas as Empresas:
    GET http://localhost:5000/companies

### Obter uma Empresa por CNPJ
    GET http://localhost:5000/companies/{cnpj}

### Criar uma Nova Empresa
    POST http://localhost:5000/companies
#### Exmplo de Body:
```
    {
        "cnpj": "13220979000155",
        "razao_social": "Nice Teste S.A.",
        "nome_fantasia": "G Services",
        "cnae": "96092"
    }
    ou
    {
        "cnpj": "13.220.979/0001-55",
        "razao_social": "Nice Teste S.A.",
        "nome_fantasia": "G Services",
        "cnae": "9609-2"
    }
````

### Atualizar uma Empresa por CNPJ
    PUT http://localhost:5000/companies/{cnpj}
#### Exmplo de Body:
```
    {
        "cnpj": "13220979000155",
        "nome_fantasia": "G New Name S.A.",
    }
````

### Excluir uma Empresa por CNPJ
    DELETE http://localhost:5000/companies/{cnpj}
