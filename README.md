<h1>Escopo</h1>
***
# Software de Gestão de Biblioteca Web

## Integrantes do Projeto

*   **Samuel Anderson Leite da Silva** – RA: 202403033097
*   **Pedro Henrique Menegatti Sandoval** – RA: 202402394932
*   **Vinicius Matos Jacomo** – RA: 202403787822
*   **Mikael Panucci Fonseca** – RA: 202504454845

***

## 1. Introdução

Este repositório contém o projeto **Software de Gestão de Biblioteca Web**, desenvolvido com o objetivo de oferecer uma solução moderna, organizada e funcional para o gerenciamento de bibliotecas.\
O sistema permite cadastrar livros, registrar empréstimos, acompanhar devoluções e visualizar relatórios essenciais para administração do acervo.

***

## 2. Objetivo do Sistema

O sistema busca:

*   Melhorar o controle do estoque de livros;
*   Automatizar o processo de empréstimo e devolução;
*   Acompanhar atrasos e prazos de entrega;
*   Disponibilizar relatórios úteis para tomada de decisão;
*   Facilitar a gestão da biblioteca por meio de uma plataforma web simples e intuitiva.

***

## 3. Escopo do Sistema

### 3.1 Controle de Estoque

O sistema permite:

*   Adicionar novos livros ao acervo;
*   Acompanhar a quantidade disponível;
*   Acompanhar a quantidade emprestada.

***

### 3.2 Status do Livro

Cada livro possui um status baseado na quantidade disponível:

*   **Disponível**
*   **Estoque Baixo**
*   **Esgotado**

***

### 3.3 Controle de Empréstimos

Funcionalidades implementadas:

*   Registrar empréstimos;
*   Registrar devoluções;
*   Prorrogar prazos (extensão futura);
*   Exibir usuários com livros atrasados;
*   Exibir livros em atraso.

***

### 3.4 Relatórios

O sistema poderá gerar relatórios como:

*   Total de livros cadastrados;
*   Livros mais emprestados;
*   Controle de caixa e multas (futuro).

***

## 4. Diagrama UML do Sistema

O diagrama abaixo representa as classes, atributos e relacionamentos exatamente como estão implementados no código Flask.

<img width="2192" height="2268" alt="image" src="https://github.com/user-attachments/assets/cc9a1d71-cb24-4c4b-9ffd-f4ca59362a11" />


***

## 5. Tecnologias Utilizadas

*   **Python 3.x**
*   **Flask** (micro framework web)
*   **HTML + Bootstrap** (templates)
*   **Mermaid** (diagramas no GitHub)

***

## 6. Estrutura Simplificada do Código

*   `app.py` → Backend em Flask
*   `templates/` → Páginas HTML
*   `static/` → CSS, JS e imagens


## 8. Considerações Finais

O **Software de Gestão de Biblioteca Web** foi desenvolvido com o objetivo de facilitar a administração de acervos e empréstimos de maneira prática e funcional.\
A estrutura modular permite melhorias futuras, como integração com banco de dados, autenticação de usuários, sistema de multas e geração de relatórios completos.

***
