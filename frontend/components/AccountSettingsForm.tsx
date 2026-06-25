"use client";

import {
  BellRing,
  Building2,
  KeyRound,
  LoaderCircle,
  Save,
  SlidersHorizontal,
  UserRound,
} from "lucide-react";
import { FormEvent, ReactNode, useState } from "react";

import type { Usuario } from "@/types/licitacao";

type AccountSettingsFormProps = {
  usuario: Usuario;
};

type SectionProps = {
  icon: ReactNode;
  title: string;
  description: string;
  children: ReactNode;
};

const fieldClass =
  "focus-ring h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-800 placeholder:text-slate-400";
const textareaClass =
  "focus-ring w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800 placeholder:text-slate-400";

function Section({ icon, title, description, children }: SectionProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
      <div className="flex items-start gap-3">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-navy-50 text-navy-700">
          {icon}
        </span>
        <div>
          <h2 className="text-xl font-bold text-navy-950">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-slate-500">{description}</p>
        </div>
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function Label({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-bold text-navy-950">
        {title}
      </span>
      {children}
    </label>
  );
}

function splitList(value: FormDataEntryValue | null): string[] {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function optionalNumber(value: FormDataEntryValue | null): number | null {
  const raw = String(value || "").trim();
  if (!raw) return null;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : null;
}

export function AccountSettingsForm({ usuario }: AccountSettingsFormProps) {
  const [saving, setSaving] = useState(false);
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setProfileMessage(null);
    setProfileError(null);
    const form = new FormData(event.currentTarget);
    const alertHours = [168, 72, 24, 2].filter(
      (hours) => form.get(`alerta_${hours}`) === "on",
    );
    const payload = {
      nome: String(form.get("nome") || ""),
      telefone: String(form.get("telefone") || "") || null,
      razao_social: String(form.get("razao_social") || "") || null,
      nome_fantasia: String(form.get("nome_fantasia") || "") || null,
      cnpj: String(form.get("cnpj") || "") || null,
      segmentos: splitList(form.get("segmentos")),
      ufs_interesse: splitList(form.get("ufs_interesse")).map((uf) =>
        uf.toUpperCase(),
      ),
      municipios_interesse: splitList(form.get("municipios_interesse")),
      valor_minimo_interesse: optionalNumber(
        form.get("valor_minimo_interesse"),
      ),
      valor_maximo_interesse: optionalNumber(
        form.get("valor_maximo_interesse"),
      ),
      palavras_chave: splitList(form.get("palavras_chave")),
      palavras_ignoradas: splitList(form.get("palavras_ignoradas")),
      modalidades_interesse: splitList(form.get("modalidades_interesse")),
      orgaos_interesse: splitList(form.get("orgaos_interesse")),
      prazo_minimo_dias: optionalNumber(form.get("prazo_minimo_dias")),
      alertar_novas_oportunidades:
        form.get("alertar_novas_oportunidades") === "on",
      alertas_antecedencia_horas: alertHours,
      frequencia_resumo: String(form.get("frequencia_resumo") || "nenhum"),
      horario_inicio_alertas: String(
        form.get("horario_inicio_alertas") || "08:00",
      ),
      horario_fim_alertas: String(
        form.get("horario_fim_alertas") || "20:00",
      ),
    };
    const response = await fetch("/api/conta/auth/me", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (response.ok) {
      setProfileMessage("Configurações salvas com sucesso.");
    } else {
      setProfileError(body.detail || "Não foi possível salvar.");
    }
    setSaving(false);
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordMessage(null);
    setPasswordError(null);
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const novaSenha = String(form.get("nova_senha") || "");
    if (novaSenha !== String(form.get("confirmar_senha") || "")) {
      setPasswordError("A confirmação não corresponde à nova senha.");
      return;
    }
    const response = await fetch("/api/conta/auth/alterar-senha", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        senha_atual: String(form.get("senha_atual") || "") || null,
        nova_senha: novaSenha,
      }),
    });
    const body = await response.json();
    if (response.ok) {
      setPasswordMessage(body.message);
      formElement.reset();
    } else {
      setPasswordError(body.detail || "Não foi possível alterar a senha.");
    }
  }

  return (
    <div className="space-y-7">
      <form onSubmit={saveProfile} className="space-y-7">
        <Section
          icon={<UserRound size={21} />}
          title="Dados pessoais"
          description="Informações básicas usadas para identificar sua conta."
        >
          <div className="grid gap-4 md:grid-cols-2">
            <Label title="Nome">
              <input
                name="nome"
                required
                minLength={2}
                defaultValue={usuario.nome}
                className={fieldClass}
              />
            </Label>
            <Label title="E-mail">
              <input
                value={usuario.email}
                disabled
                className={`${fieldClass} bg-slate-50 text-slate-500`}
              />
            </Label>
            <Label title="Telefone">
              <input
                name="telefone"
                defaultValue={usuario.telefone || ""}
                placeholder="(00) 00000-0000"
                className={fieldClass}
              />
            </Label>
          </div>
        </Section>

        <Section
          icon={<Building2 size={21} />}
          title="Dados da empresa"
          description="Esses dados servirão para personalizar oportunidades e compatibilidade."
        >
          <div className="grid gap-4 md:grid-cols-2">
            <Label title="Razão social">
              <input
                name="razao_social"
                defaultValue={usuario.razao_social || ""}
                className={fieldClass}
              />
            </Label>
            <Label title="Nome fantasia">
              <input
                name="nome_fantasia"
                defaultValue={usuario.nome_fantasia || ""}
                className={fieldClass}
              />
            </Label>
            <Label title="CNPJ">
              <input
                name="cnpj"
                defaultValue={usuario.cnpj || ""}
                placeholder="00.000.000/0000-00"
                className={fieldClass}
              />
            </Label>
            <Label title="Segmentos de atuação">
              <input
                name="segmentos"
                defaultValue={usuario.segmentos.join(", ")}
                placeholder="software, engenharia, saúde"
                className={fieldClass}
              />
            </Label>
            <Label title="UFs atendidas">
              <input
                name="ufs_interesse"
                defaultValue={usuario.ufs_interesse.join(", ")}
                placeholder="SP, MG, RJ"
                className={fieldClass}
              />
            </Label>
            <Label title="Municípios atendidos">
              <input
                name="municipios_interesse"
                defaultValue={usuario.municipios_interesse.join(", ")}
                placeholder="São Paulo, Campinas"
                className={fieldClass}
              />
            </Label>
            <Label title="Valor mínimo de interesse">
              <input
                type="number"
                min="0"
                step="0.01"
                name="valor_minimo_interesse"
                defaultValue={usuario.valor_minimo_interesse || ""}
                className={fieldClass}
              />
            </Label>
            <Label title="Valor máximo de interesse">
              <input
                type="number"
                min="0"
                step="0.01"
                name="valor_maximo_interesse"
                defaultValue={usuario.valor_maximo_interesse || ""}
                className={fieldClass}
              />
            </Label>
          </div>
        </Section>

        <Section
          icon={<SlidersHorizontal size={21} />}
          title="Preferências de oportunidades"
          description="Separe vários termos por vírgula. Usaremos isso nos alertas personalizados."
        >
          <div className="grid gap-4 md:grid-cols-2">
            <Label title="Palavras-chave desejadas">
              <textarea
                name="palavras_chave"
                rows={3}
                defaultValue={usuario.palavras_chave.join(", ")}
                placeholder="software, equipamentos médicos"
                className={textareaClass}
              />
            </Label>
            <Label title="Palavras que devem ser ignoradas">
              <textarea
                name="palavras_ignoradas"
                rows={3}
                defaultValue={usuario.palavras_ignoradas.join(", ")}
                placeholder="obra, combustível"
                className={textareaClass}
              />
            </Label>
            <Label title="Modalidades de interesse">
              <input
                name="modalidades_interesse"
                defaultValue={usuario.modalidades_interesse.join(", ")}
                placeholder="pregão eletrônico, concorrência"
                className={fieldClass}
              />
            </Label>
            <Label title="Órgãos de interesse">
              <input
                name="orgaos_interesse"
                defaultValue={usuario.orgaos_interesse.join(", ")}
                placeholder="prefeituras, secretarias de saúde"
                className={fieldClass}
              />
            </Label>
            <Label title="Prazo mínimo para participar">
              <div className="relative">
                <input
                  type="number"
                  min="0"
                  max="365"
                  name="prazo_minimo_dias"
                  defaultValue={usuario.prazo_minimo_dias ?? ""}
                  className={`${fieldClass} pr-16`}
                />
                <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm text-slate-400">
                  dias
                </span>
              </div>
            </Label>
          </div>
        </Section>

        <Section
          icon={<BellRing size={21} />}
          title="Preferências de notificações"
          description="Defina quais avisos deseja receber e em quais horários."
        >
          <label className="flex items-start gap-3 rounded-xl bg-slate-50 p-4">
            <input
              type="checkbox"
              name="alertar_novas_oportunidades"
              defaultChecked={usuario.alertar_novas_oportunidades}
              className="mt-1 h-4 w-4 accent-navy-900"
            />
            <span>
              <span className="block font-bold text-navy-950">
                Novas oportunidades compatíveis
              </span>
              <span className="mt-1 block text-sm text-slate-500">
                Avisar quando uma nova licitação corresponder às preferências.
              </span>
            </span>
          </label>

          <fieldset className="mt-5">
            <legend className="text-sm font-bold text-navy-950">
              Avisar antes do encerramento
            </legend>
            <div className="mt-3 flex flex-wrap gap-3">
              {[
                [168, "7 dias"],
                [72, "3 dias"],
                [24, "24 horas"],
                [2, "2 horas"],
              ].map(([hours, label]) => (
                <label
                  key={hours}
                  className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold"
                >
                  <input
                    type="checkbox"
                    name={`alerta_${hours}`}
                    defaultChecked={usuario.alertas_antecedencia_horas.includes(
                      Number(hours),
                    )}
                    className="h-4 w-4 accent-navy-900"
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <Label title="Resumo de oportunidades">
              <select
                name="frequencia_resumo"
                defaultValue={usuario.frequencia_resumo}
                className={fieldClass}
              >
                <option value="nenhum">Não enviar resumo</option>
                <option value="diario">Resumo diário</option>
                <option value="semanal">Resumo semanal</option>
              </select>
            </Label>
            <Label title="Enviar alertas a partir de">
              <input
                type="time"
                name="horario_inicio_alertas"
                defaultValue={usuario.horario_inicio_alertas}
                className={fieldClass}
              />
            </Label>
            <Label title="Enviar alertas até">
              <input
                type="time"
                name="horario_fim_alertas"
                defaultValue={usuario.horario_fim_alertas}
                className={fieldClass}
              />
            </Label>
          </div>
        </Section>

        <div className="sticky bottom-4 z-20 flex flex-col items-end gap-2">
          {profileMessage ? (
            <p className="rounded-lg bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-700 shadow">
              {profileMessage}
            </p>
          ) : null}
          {profileError ? (
            <p className="rounded-lg bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 shadow">
              {profileError}
            </p>
          ) : null}
          <button
            disabled={saving}
            className="focus-ring inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-navy-900 px-6 font-bold text-white shadow-lg disabled:opacity-60"
          >
            {saving ? (
              <LoaderCircle className="animate-spin" size={18} />
            ) : (
              <Save size={18} />
            )}
            Salvar configurações
          </button>
        </div>
      </form>

      <Section
        icon={<KeyRound size={21} />}
        title="Segurança"
        description="Troque sua senha regularmente e não reutilize senhas de outros serviços."
      >
        <form
          onSubmit={changePassword}
          className="grid gap-4 md:grid-cols-3"
        >
          {usuario.tem_senha ? (
            <Label title="Senha atual">
              <input
                type="password"
                name="senha_atual"
                required
                autoComplete="current-password"
                className={fieldClass}
              />
            </Label>
          ) : (
            <div className="rounded-xl bg-sky-50 p-4 text-sm leading-6 text-sky-900">
              Sua conta usa login com Google. Você pode criar uma senha para
              também entrar por e-mail.
            </div>
          )}
          <Label title="Nova senha">
            <input
              type="password"
              name="nova_senha"
              required
              minLength={8}
              autoComplete="new-password"
              className={fieldClass}
            />
          </Label>
          <Label title="Confirmar nova senha">
            <input
              type="password"
              name="confirmar_senha"
              required
              minLength={8}
              autoComplete="new-password"
              className={fieldClass}
            />
          </Label>
          <div className="md:col-span-3">
            {passwordMessage ? (
              <p className="mb-3 text-sm font-semibold text-emerald-700">
                {passwordMessage}
              </p>
            ) : null}
            {passwordError ? (
              <p className="mb-3 text-sm font-semibold text-red-700">
                {passwordError}
              </p>
            ) : null}
            <button className="focus-ring rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-navy-900 hover:bg-slate-50">
              {usuario.tem_senha ? "Alterar senha" : "Criar senha"}
            </button>
          </div>
        </form>
      </Section>
    </div>
  );
}
