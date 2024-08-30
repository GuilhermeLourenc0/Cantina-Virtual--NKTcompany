CREATE DATABASE bd_cantinadalu;

USE bd_cantinadalu;

-- Ajustando a tabela tb_cliente
CREATE TABLE tb_curso (
    id_curso INT AUTO_INCREMENT,
    curso VARCHAR(50),
    PRIMARY KEY (id_curso)
);

-- Tabela de Clientes
CREATE TABLE tb_cliente (
    id_cliente INT AUTO_INCREMENT,
    nome_comp VARCHAR(100),
    telefone VARCHAR(15),
    email VARCHAR(100),
    id_curso INT,  -- Nova coluna para referência ao curso
    senha VARCHAR(50),
    tipo VARCHAR(20), 
    PRIMARY KEY (id_cliente),
    FOREIGN KEY (id_curso) REFERENCES tb_curso(id_curso)
);
-- Ajustando a tabela tb_produto
CREATE TABLE tb_produto (
 cod_produto INT AUTO_INCREMENT,
 nome_produto VARCHAR(100),
 preco DECIMAL(10,2),
 url_img VARCHAR(255),
 descricao TEXT,
 PRIMARY KEY (cod_produto)
);

-- Ajustando a tabela tb_avaliacao
CREATE TABLE tb_avaliacao (
 id_aval INT AUTO_INCREMENT, 
 cod_produto INT NOT NULL,  
 avaliacao DECIMAL(3,2),
 PRIMARY KEY (id_aval, cod_produto),
 FOREIGN KEY (cod_produto) REFERENCES tb_produto (cod_produto)
);

-- Ajustando a tabela tb_carrinho
CREATE TABLE tb_carrinho (
 id_carrinho INT AUTO_INCREMENT,
 cod_produto INT NOT NULL,  -- Mudança de VARCHAR para INT
 id_cliente INT NOT NULL,
 PRIMARY KEY (id_carrinho),
 FOREIGN KEY (cod_produto) REFERENCES tb_produto (cod_produto),
 FOREIGN KEY (id_cliente) REFERENCES tb_cliente (id_cliente)
);

-- Ajustando a tabela tb_categoria
CREATE TABLE tb_categoria (
 id_categoria INT AUTO_INCREMENT, 
 cod_produto INT NOT NULL,  -- Mudança de VARCHAR para INT
 nome VARCHAR(50), 
 PRIMARY KEY (id_categoria, cod_produto),
 FOREIGN KEY (cod_produto) REFERENCES tb_produto (cod_produto)
);
