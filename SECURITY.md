# Política de segurança

O Zircon funciona sem internet. A única conexão que ele faz é a verificação de atualizações, e só quando você clica em "Ajuda > Verificar atualizações". Essa verificação consulta a página de versões do GitHub e não envia nenhum dado seu. Os detalhes estão em [docs/arquitetura_e_privacidade.md](docs/arquitetura_e_privacidade.md).

## Versões com correções de segurança

Só a versão mais recente recebe correções. Se você usa uma versão antiga, atualize antes de relatar um problema.

| Versão | Recebe correções |
| ------ | ---------------- |
| A mais recente (veja [Releases](https://github.com/cibelegeologia/zircon/releases/latest)) | ✅ |
| Todas as anteriores | ❌ |

## Como relatar uma vulnerabilidade

**Não abra uma issue pública**, porque ela fica visível para todos antes de existir uma correção.

1. Abra a aba **Security** do repositório e clique em **Report a vulnerability**. O relato fica privado, visível só para você e para a mantenedora.
2. Conte o que encontrou, em português, inglês ou espanhol. Inclua:
   - a versão do Zircon e o sistema (Windows, macOS ou Linux);
   - os passos para reproduzir o problema;
   - o que pode acontecer se alguém se aproveitar dele.
3. Não inclua dados de pesquisa não publicados. Se precisar de um arquivo de exemplo, use dados inventados.

O Zircon é um projeto voluntário. As respostas e as correções são feitas no melhor esforço possível, sem prazo garantido. Se o problema for confirmado, a correção sai numa versão nova, que o [CHANGELOG](CHANGELOG.md) registra, com crédito a quem relatou, se a pessoa quiser. Se não for confirmado, você recebe uma explicação no próprio relato.

---

## Security policy (summary in English)

Zircon works offline. Its only network access is the update check, which runs only when the user clicks "Help > Check for updates" and sends no user data.

- **Supported versions:** only the [latest release](https://github.com/cibelegeologia/zircon/releases/latest) receives security fixes.
- **Reporting:** please do **not** open a public issue. Use the repository's **Security** tab, then **Report a vulnerability**, so the report stays private. Include the Zircon version, your operating system, steps to reproduce, and the possible impact. Do not include unpublished research data.
- **Response:** this is a volunteer project. Reports are handled on a best-effort basis, with no guaranteed response time. Confirmed issues are fixed in a new release and noted in the CHANGELOG.
