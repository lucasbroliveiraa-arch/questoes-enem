# Status da implementação

A versão entregue neste diretório implementa as decisões consolidadas dos
Pontos 1 e 2 e as pendências de código da v1.

## Validado automaticamente

- 19 testes pytest passando.
- migrations executadas em SQLite.
- migração de dados legados testada.
- seed incremental testado em duas execuções.
- explicação interna preservada no segundo seed.
- JavaScript validado com `node --check`.
- Python validado com `compileall`.

## Ainda depende do ambiente

- PostgreSQL real via Docker.
- dataset real em `data-source/`.
- inspeção visual/performance no navegador.
- GitHub remoto.
- provedor de hospedagem/domínio.

Consulte `docs/05-implementacao-v1.md`.
