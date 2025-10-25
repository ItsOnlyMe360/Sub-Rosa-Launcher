# Sub Rosa-Launcher Alpha 24
Esse programa tem uma funciona de forma simples.
Basicamente ele tem uma pasta ``instances`` com pastas ``sr_nomedomapa`` que têm executaveis do Sub Rosa, cada pasta tem um executavel com um mapa diferente, cada pasta também tem um ``map.json`` que tem metadados do mapa como nome, descrição e tags, agora ele indexa isso tudo no programa e mostra uma lista de seleção, ao selecionar um mapa e clicar em jogar, ele vai abrir o ``subrosa.exe`` do mapa selecionado, bem simples.
O programa também conta com um importador de mapas, basta selecionar um arquivo ``.srmap`` e importar pro programa, ele adiciona a lista de mapas e é só jogar.

## Detalhes
O formato ``.srmap`` nada mais é do que um ``.zip`` renomeado, a estrutura de pasta dentro do zip é simples, é o ``sr_`` com os arquivos dentro.
O programa só vai identificar um mapa se a pasta dentro de ``instances`` houver ``sr_`` no começo, se não estiver exatamente assim ele não vai ver.
O programa também não vai identificar um mapa se não houver ``map.json`` dentro do ``sr_`` portanto os metadados são obrigatórios, por sinal essa é a formatação:

```
{
  "name": "Cidade Padrão",
  "description": "A cidade padrão do SubRosa 24.",
  "tags": ["world", "rounds"]
}
```

As tags não são predefinidas então qualquer coisa pode ser escrita nelas, nesse exemplo e no que eu pessoalmente acho melhor pro uso delas é a identificação de quais modos servem pra quais mapas.

## Rodando o código
Você precisa instalar o PyQt6, basta dar ``pip install PyQt6`` no console.

## Futuro em relação a funcionalidade e segurança
Ter várias cópias diferentes do jogo é inviável e inseguro em relação a exportação e importação de mapas por conta de executar os exes individualmente, então pessoas mal intencionadas podem trocar esse exe por algum que contenha conteúdo malicioso, então não importe mapas que você não confie, por conta disso, futuramente o programa vai ter a base do Sub Rosa com apenas um exe padrão e vai puxar apenas arquivos de mapa, substituindo eles antes de executar o jogo.

### Código gerado usando IA (Google AI Studio)
