# 🤖 Ansible Playbook — Stack de IA Self-Hosted no Proxmox VE

Playbook idempotente para provisionar do zero a stack completa:
**Proxmox host → VMs/LXCs → NVIDIA + Ollama → Open WebUI → Traefik/Authentik → Observabilidade.**

---

## 📋 Pré-requisitos

- **Workstation de controle** com Ansible >= 2.16 e Python 3.10+
- Acesso SSH por chave ao host **Proxmox VE 8.x** (`root@pve.local`)
- Hardware-alvo: 28 vCPU / 128 GB RAM / RTX 3060 12 GB
- Domínio interno resolvível (ex.: `*.empresa.local` via DNS corporativo)

---

## 🚀 Quickstart (5 passos)

### 1) Clonar e instalar dependências

```bash
git clone <seu-repo>/ansible-ai-stack.git
cd ansible-ai-stack

# Coleções Ansible
ansible-galaxy collection install -r requirements.yml
```

### 2) Configurar inventário

Edite `inventory/hosts.yml` com os IPs do seu ambiente (default: rede `10.10.10.0/24`).

### 3) Configurar secrets (Ansible Vault)

```bash
cp group_vars/vault.yml.example group_vars/vault.yml
$EDITOR group_vars/vault.yml      # preencha os secrets

# Criptografar
ansible-vault encrypt group_vars/vault.yml
```

### 4) Executar o playbook completo

```bash
ansible-playbook site.yml --ask-vault-pass
```

> ⏱️ Tempo total: 3–5h (downloads de modelos via Ollama é o gargalo).

### 5) Acessar

- Open WebUI: https://ai.empresa.local
- Authentik (SSO admin): https://auth.empresa.local
- Grafana: http://10.10.10.21:3001

---

## 🎯 Execução por etapas (tags)

| Tag | O que executa | Quando usar |
|-----|--------------|-------------|
| `pve` / `iommu` | Configura IOMMU + VFIO no host PVE | 1ª vez (requer reboot) |
| `provision` | Cria VMs e LXCs no PVE | Após reboot do host |
| `inference` | NVIDIA + Ollama + modelos | Stack de IA |
| `apps` | Open WebUI + RAG | Frontend |
| `edge` | Traefik + Authentik | SSO/HTTPS |
| `observ` | Prometheus + Grafana + Loki | Monitoring |

```bash
# Exemplos
ansible-playbook site.yml --tags pve --ask-vault-pass
ansible-playbook site.yml --tags "inference,apps" --ask-vault-pass
ansible-playbook site.yml --tags edge --ask-vault-pass --check  # dry-run
```

---

## 🔐 Operando o Vault

```bash
# Editar secrets já criptografados
ansible-vault edit group_vars/vault.yml

# Trocar a senha do vault
ansible-vault rekey group_vars/vault.yml

# Visualizar
ansible-vault view group_vars/vault.yml

# Usar arquivo de senha (CI/CD)
echo "$VAULT_PASS" > ~/.vault_pass
chmod 600 ~/.vault_pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

---

## 🗂️ Estrutura

```
ansible-ai-stack/
├── ansible.cfg
├── requirements.yml
├── site.yml                       # Master playbook
├── inventory/hosts.yml
├── group_vars/
│   ├── all.yml                    # Vars não-sensíveis
│   └── vault.yml                  # Vars sensíveis (criptografadas)
├── playbooks/
│   ├── 00-pve-host.yml            # IOMMU/VFIO
│   ├── 01-provision-guests.yml    # VMs + LXCs
│   ├── 02-ai-inference.yml        # NVIDIA + Ollama
│   ├── 03-ai-apps.yml             # Open WebUI + RAG
│   ├── 04-edge.yml                # Traefik + Authentik
│   └── 05-observability.yml       # Prometheus + Grafana + Loki
└── roles/
    ├── pve_iommu/
    ├── pve_provision_vm/
    ├── pve_provision_lxc/
    ├── nvidia_driver/
    ├── ollama/
    ├── docker/
    ├── ai_apps_stack/
    ├── edge_stack/
    └── observability_stack/
```

---

## 🛠️ Troubleshooting

| Sintoma | Causa provável | Correção |
|---------|----------------|----------|
| `proxmox_kvm` falha autenticando | Vault errado | `ansible-vault view group_vars/vault.yml` |
| Reboot loop após `pve_iommu` | IOMMU não suportado pela BIOS | Habilitar VT-d / AMD-Vi |
| `nvidia-smi` falha | Driver não carregou após reboot | `--tags inference` re-executa idempotentemente |
| Ollama lento | Modelos rodando na CPU | Verificar `nvidia-smi` na VM e re-run `--tags inference` |
| Compose não sobe | Variáveis vazias | Verificar `group_vars/vault.yml` |
| SSH timeout pós-reboot | Reboot do PVE em curso | Aguardar 2 min e re-executar |

```bash
# Debug verboso
ansible-playbook site.yml -vvv --ask-vault-pass

# Limit a um único host
ansible-playbook site.yml --limit vm-ai-inference --ask-vault-pass

# Modo step (confirma cada task)
ansible-playbook site.yml --step --ask-vault-pass
```

---

## 📚 Próximos passos pós-deploy

1. Criar conta no Authentik → configurar OIDC Application para Open WebUI
2. No Open WebUI, ajustar `num_ctx=32768` em cada modelo (RAG/Web Search)
3. Criar grupos `devs` e `geral` com RBAC
4. Distribuir `~/.continue/config.yaml` (consulte `examples/continue-config.yaml`)
5. Importar dashboards Grafana

---

**Licença:** MIT · **Autor:** Arquitetura Corporativa
