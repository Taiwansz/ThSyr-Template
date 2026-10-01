---
id: node-redes-corporativas
type: discipline-technical
tags:
  - infraestrutura
  - redes
  - cisco
  - parietal
---

# Redes Corporativas e Infraestrutura L2/L3

Modulo tecnico de infraestrutura, conectividade e arquitetura de redes corporativas focado em switching L2/L3, protocolos industriais e resiliencia.

## Sinapses
- Conectada a [[Lobo_Parietal]] e [[Padroes_Engenharia]].

## Metodologia de Enderecamento e Calculo de Sub-redes
- Instrucao empirica e concreta: metodo do Numero Magico (`256 - mascara`).
- Regua de potencias de 2 (`128, 64, 32, 16, 8, 4, 2, 1`), acelerando calculos de VLSM e CIDR.

## Pilares e Topologias Consolidadas
1. **Segregação L2 via VLANs**:
   - Isolamento de domínios de broadcast (VLANs administrativas, operacionais e de gestao).
   - Segurança L2: Desativação de tráfego de dados na VLAN 1 default e criação de VLAN nativa dedicada para Trunks 802.1Q.
2. **Trunking e Agregação**:
   - Trunks IEEE 802.1Q com pruning de VLANs permitidas.
   - EtherChannel (LACP 802.3ad) para redundância e agregação de largura de banda.
3. **Simulação e Modelagem**:
   - Simulações topológicas e automação de scripts de configuração em switches e roteadores.
