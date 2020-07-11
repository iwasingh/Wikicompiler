<br />
 p align="center">
  <a href="https://github.com/iwasingh/Wikicompiler">
    <img src="https://i.imgur.com/fcuaUFj.png" alt="Logo" width="425px">
  </a>

  <h3 align="center">Wikicompiler </h3>

  <p align="center">
    Wikitext compiler
<br />

# Wikicompiler

Wikicompiler is a fully extensible library that helps you to compile [Wikitext](https://www.mediawiki.org/wiki/Wikitext). For example you can do text analysis, text extraction, document preprocessing and so on. In fact this library implements a recursive descent parser that parse and evaluate(you can custumize this process if you want) the wikicode. Check out the examples

## Basic Usage
```
 from wikicompiler import compiler as c
 
 wcc = c.Compiler()
 wcc.compile(text)
 
```
You can listen specific events emitted by the compiler. Let's say you want to grab all the links from a page:

```
 links = []
 wcc.on(lambda node: links.append(node), c.ParseTypes.LINK) 

```
Done! Checkout the examples section for more infos [Link extraction](https://github.com/iwasingh/Wikicompiler/tree/master/examples)

### AST

If you want the AST instead, you can do the following way
```
 from wikicompiler import parser.parser as p
 
 text="==Hello World=="
 parser = p.Parser()
 ast = parser.parse(text)

```

### Grammar
You can pass your own grammar to the parse and evaluate the AST yourself. Furthermore you can you the combinators to write your own rules checkout the [Grammar](https://github.com/iwasingh/Wikicompiler/blob/master/parser/grammar.py) and the [combinators](https://github.com/iwasingh/Wikicompiler/blob/master/utils/combinators.py)

```python

 class MyGrammar:
  # This is important! The parser will consider this as a starting symbol
  def expression(self):
    # Must return a function that accept a parser
    return seq(expect(Heading2.start), self.mytext, expect(Heading2.end))
  
  def mytext(self):
    return p.Node(p.TextP('My static node'))
    
 
 parser = Parser(grammar=MyGrammar.expression())
 parser.parse(text)

```

