CREATE DATABASE bd_cantinadalu;

USE bd_cantinadalu;

-- Tabela de Cursos
CREATE TABLE tb_curso (
    id_curso INT AUTO_INCREMENT,
    curso VARCHAR(255),
    PRIMARY KEY (id_curso)
);

-- Tabela de Clientes
CREATE TABLE tb_cliente (
    id_cliente INT AUTO_INCREMENT,
    nome_comp VARCHAR(100),
    telefone VARCHAR(15),
    email VARCHAR(100),
    id_curso INT,  -- Nova coluna para referência ao curso
    senha VARCHAR(255),
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

INSERT INTO tb_curso (curso) VALUES ('CLP SIEMENS - TIA Portal - CLPTIA-2A24'),
('Comandos Elétricos - COMANDOS-2A24'),
('ELETRICISTA DE REDE DE DISTRIBUIÇÃO DE ENERGIA ELÉTRICA - 153/2024-ERDEE'),
('Fabricação de pães e Salgados Fitness - 221/2024-SEBRAE'),
('Fundamentos de Ciência de Dados - Google Cloud - GR-G.CLOUD-2B24'),
('Fundamentos de Ciência de Dados - Google Cloud - GR-G.CLOUD-2C24'),
('Implantação de Serviços em Nuvem - AWS Cloud Practitioner Foundational - GR-PLAT.AWS2A24'),
('Implantação de Serviços em Nuvem - AWS Cloud Practitioner Foundational - GR-PLAT.AWS2B24'),
('Implantação de Serviços em Nuvem - Microsoft AZ-900 - GR-AZ900-2A24'),
('Massas Folhadas e Semi-Folhadas - GR-MASS-GP-2B24'),
('Microsoft Office Specialist Associate - GR-MOFFICE-1A24'),
('Microsoft Office Specialist Associate - GR-MOFFICE-1B24'),
('Microsoft Office Specialist Associate - GR-MOFFICE-1C24'),
('Microsoft Power BI - GR-MPBI-2F24'),
('Móveis Clássicos - GR-MOVCLA-2A24'),
('NR-11 - Operação de Empilhadeira - EMPILHAD-2A24'),
('NR11- OPERAÇÃO DE REBOCADOR DESEMBARCADO REMOTO - 170/2024-ORDR'),
('Operação Ferroviária - 95/2024-OF-N'),
('Operação Ferroviária - 95/2024-OF-T'),
('Orientador de Práticas na Empresa - ORI-PRAT-2A24'),
('Power BI - GR-PBI-2E24'),
('Programação em Python - GR-PYTHON-2A24'),
('Programação em Python - GR-PYTHON-S2B24'),
('Almoxarife - N2-Almox'),
('Assistente Administrativo - M2-ASSIST'),
('Assistente Administrativo - T1-ASSIST-Usina'),
('Assistente Administrativo - T2-ASSIST'),
('Assistente de Logística - T1-Assist. Log'),
('Auxiliar de Linha de Produção - M2-Aux.Prod'),
('Auxiliar de Linha de Produção - N1-Aux.Prod'),
('Auxiliar de Linha de Produção - N2-Aux.Prod'),
('Auxiliar de Linha de Produção - T2-Aux.Prod'),
('Caldeireiro - 4CM'),
('Caldeireiro - 4CT'),
('Confeccionador de Embalagens Plásticas - T1-Emb.Plástica'),
('Confeccionador de Peças de Enxoval e Afins - M2CONFEC-C'),
('Confeccionador de Peças de Enxoval e Afins - M3CONFEC-A'),
('Confeccionador de Peças de Enxoval e Afins - M3CONFEC-B'),
('Confeccionador de Peças de Enxoval e Afins - T1CONFEC-A'),
('Confeccionador de Peças de Enxoval e Afins - T1CONFEC-B'),
('Confeccionador de Roupas - M1-Conf.Roupas'),
('Confeccionador de Roupas - M2-Conf.Roupas'),
('Confeccionador de Roupas - N2-Conf.Roupas'),
('Confeccionador de Roupas - T1-Conf.Roupas'),
('Confeccionador de Roupas - T2-Conf.Roupas'),
('Eletricista de Manutenção Eletroeletrônica - M2E-Usina'),
('Eletricista de Manutenção Eletroeletrônica - M2F'),
('Ferramenteiro de Corte, Dobra e Repuxo - 4FM'),
('Mecânico de Automóveis Leves - M2C-Usina'),
('Mecânico de Automóveis Leves - T4C'),
('Mecânico de Manutenção - 4MMM'),
('Mecânico de Manutenção - 4MMT'),
('Mecânico de Manutenção de Máquinas de Costura - N3-MCOST'),
('Mecânico de Manutenção de Teares - M1L-Lupo'),
('Mecânico de Manutenção de Teares - T2L'),
('Mecânico de Manutenção de Veículos Pesados Rodoviários - M4C'),
('Mecânico de Manutenção de Veículos Pesados Rodoviários - T2C'),
('Mecânico de Usinagem - M2A'),
('Mecânico de Usinagem - M4B'),
('Mecânico de Usinagem - T2A'),
('Montador de Sistemas de Aeronaves - 1T-MSA'),
('Soldador - 1SM-Randon'),
('Soldador - 2ST'),
('Técnico em Eletroeletrônica - 4ELT'),
('Técnico em Logística - 2LOGN'),
('TÉCNICO EM MANUTENÇÃO AUTOMOTIVA - 1AUT-SM-EAD'),
('TÉCNICO EM MANUTENÇÃO AUTOMOTIVA - 2AUT-SM-EAD'),
('Técnico em Mecatrônica - 4MCN'),
('Técnico em Mecatrônica - 4MCT'),
('Fundamentos de Máquinas Agrícolas e Veículos Pesados - 154/2024-FMAVP1'),
('Técnico em Desenvolvimento de Sistemas - 1DS-SESI'),
('Técnico em Desenvolvimento de Sistemas - 2DS-SESI'),
('Técnico em Eletroeletrônica - 1EL-A-GOV'),
('Técnico em Eletroeletrônica - 1EL-B-GOV'),
('Técnico em Eletromecânica - 1EM-SESI'),
('Técnico em Eletromecânica - 2EM-SESI'),
('Técnico em Logística - 1LOG-SESI'),
('Técnico em Mecatrônica - 1MC-GOV'),
('Assistente de Modelagem Industrial de Roupas - GR-ASMO-SL-1A24'),
('Auxiliar Administrativo - GR-ADM-1C24'),
('Auxiliar de Produção Aeronáutica - 115/2024-APA-N'),
('Auxiliar de Produção Aeronáutica - 115/2024-APA-S'),
('Auxiliar de Produção Aeronáutica - AUX-AERO-1A24'),
('Auxiliar Mecânico de Manutenção - 95/2024-AMM-N1'),
('Auxiliar Mecânico de Manutenção - AUX-MEC-2A24'),
('Caldeireiro Montador - CALD-M-2A24'),
('Caldeireiro Traçador - GR-CALD.T-2A24'),
('Construtor de Móveis por meio de Processos Convencionais - MOVEIS-2A24'),
('Construtor de Móveis por meio de Processos Convencionais - MOVEIS-2B24'),
('Costureiro de Máquina Reta e Overloque - GR-COST-KP-1D24'),
('Costureiro de Máquina Reta e Overloque - GR-COST-KP-1E24'),
('Costureiro de Máquina Reta e Overloque - GR-COST-S-1A24'),
('Eletricista Automotivo de Veículos Leves - ELET-AUTO-2A24'),
('Eletricista Automotivo de Veículos Leves - ELET-AUTO-2B24'),
('Eletricista Instalador - 95/2024-EL-N'),
('Eletricista Instalador - ELETRICA-2A24'),
('Eletricista Instalador - ELETRICA-S-2B24'),
('Mecânico de Motor Ciclo Diesel - DIESEL-2A24'),
('Mecânico de Motor Ciclo Otto - OTTO-2A24'),
('Mecânico de Motor Ciclo Otto - OTTO-2B24'),
('Operador de Logística - OP-LOG-2A24'),
('OPERADOR DE MÁQUINAS DE USINAGEM CONVENCIONAIS - OPMUSI-2A24'),
('Operador de Máquinas e Implementos Agrícolas - 24/2024-M'),
('Operador de Máquinas e Implementos Agrícolas - 24/2024-T'),
('Soldador ao Arco Elétrico e Oxigás - SOLDA-S-2C24'),
('Torneiro Mecânico - TORNO-2A24');

select * from tb_cliente