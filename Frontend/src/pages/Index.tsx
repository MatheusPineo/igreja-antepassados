import { useState } from "react";
import { Eye, EyeOff, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import { toast } from "sonner";
import logo from "@/assets/logo.png";

type Mode = "login" | "signup";

const Index = () => {
  const [mode, setMode] = useState<Mode>("login");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const isLogin = mode === "login";

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const data = await api.googleAuth(credentialResponse.credential);
      localStorage.setItem("user", JSON.stringify(data.user));
      toast.success("Login com Google realizado!");
      navigate("/dashboard");
    } catch (error: any) {
      toast.error("Erro no login com Google: " + error.message);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const data = await api.login({ email, password });
        localStorage.setItem("user", JSON.stringify(data.user));
        toast.success("Bem-vindo!");
        navigate("/dashboard");
      } else {
        if (password !== confirmPassword) {
          toast.error("As senhas não coincidem");
          return;
        }
        await api.register({ 
          email, 
          password, 
          nome_completo: email.split('@')[0],
          aceitou_termos: true 
        });
        toast.success("Conta criada! Por favor, faça login.");
        setMode("login");
      }
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen w-full overflow-hidden bg-background">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 50% -10%, hsl(var(--primary) / 0.10), transparent 60%), radial-gradient(ellipse 60% 50% at 50% 110%, hsl(var(--primary) / 0.06), transparent 60%)",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.5]"
        style={{
          backgroundImage:
            "linear-gradient(hsl(var(--border)) 1px, transparent 1px)",
          backgroundSize: "100% 120px",
          maskImage:
            "linear-gradient(to bottom, transparent, black 25%, black 75%, transparent)",
        }}
      />

      <section className="relative z-10 flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center text-center">
            <img
              src={logo}
              alt="Igreja Messiânica Mundial de Portugal"
              width={88}
              height={88}
              className="h-20 w-20 object-contain"
            />
            <h1 className="mt-6 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              {isLogin ? "Entrar na conta" : "Criar conta"}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {isLogin
                ? "Insira o seu email e senha para continuar."
                : "Preencha os campos abaixo para começar."}
            </p>
          </div>

          <div className="mb-6 flex justify-center">
            <div className="inline-flex h-9 items-center rounded-full border border-border bg-muted/50 p-1 text-sm">
              {(["login", "signup"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={cn(
                    "h-7 rounded-full px-4 font-medium transition-smooth",
                    mode === m
                      ? "bg-card text-foreground shadow-soft"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {m === "login" ? "Entrar" : "Cadastrar"}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label
                htmlFor="email"
                className="text-xs font-medium text-muted-foreground"
              >
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                autoComplete="email"
                required
                className="h-11 rounded-lg border-border bg-card text-sm text-foreground placeholder:text-muted-foreground/60 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/15"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label
                  htmlFor="password"
                  className="text-xs font-medium text-muted-foreground"
                >
                  Senha
                </Label>
                {isLogin && (
                  <a
                    href="#"
                    className="text-xs font-medium text-primary underline-offset-4 transition-smooth hover:underline"
                  >
                    Esqueci a senha
                  </a>
                )}
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  required
                  className="h-11 rounded-lg border-border bg-card pr-11 text-sm text-foreground placeholder:text-muted-foreground/60 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/15"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-md p-2 text-muted-foreground transition-smooth hover:bg-muted hover:text-foreground"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <div
              className={cn(
                "grid overflow-hidden transition-all duration-500 ease-out",
                isLogin
                  ? "grid-rows-[0fr] opacity-0"
                  : "grid-rows-[1fr] opacity-100"
              )}
            >
              <div className="min-h-0">
                <div className="space-y-2">
                  <Label
                    htmlFor="confirm"
                    className="text-xs font-medium text-muted-foreground"
                  >
                    Confirme a senha
                  </Label>
                  <div className="relative">
                    <Input
                      id="confirm"
                      type={showConfirm ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      autoComplete="new-password"
                      disabled={isLogin}
                      required={!isLogin}
                      className="h-11 rounded-lg border-border bg-card pr-11 text-sm text-foreground placeholder:text-muted-foreground/60 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/15"
                    />
                    <button
                      type="button"
                      tabIndex={isLogin ? -1 : 0}
                      onClick={() => setShowConfirm((v) => !v)}
                      aria-label={
                        showConfirm ? "Ocultar senha" : "Mostrar senha"
                      }
                      className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-md p-2 text-muted-foreground transition-smooth hover:bg-muted hover:text-foreground"
                    >
                      {showConfirm ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="group h-11 w-full rounded-lg bg-primary text-sm font-medium text-primary-foreground shadow-soft transition-smooth hover:bg-[hsl(var(--primary-hover))] hover:shadow-elegant"
            >
              <span className="inline-flex items-center gap-2">
                {isLogin ? (loading ? "Entrando..." : "Entrar") : (loading ? "Criando..." : "Criar conta")}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </span>
            </Button>

            <div className="flex items-center gap-3 pt-1">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs text-muted-foreground">Ou</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => toast.error("Falha na autenticação com Google")}
                useOneTap
                theme="outline"
                shape="pill"
                locale="pt_PT"
              />
            </div>

            <p className="pt-2 text-center text-sm text-muted-foreground">
              {isLogin ? "Não tem conta?" : "Já tem conta?"}{" "}
              <button
                type="button"
                onClick={() => setMode(isLogin ? "signup" : "login")}
                className="font-medium text-primary underline-offset-4 transition-smooth hover:underline"
              >
                {isLogin ? "Cadastre-se" : "Entrar"}
              </button>
            </p>
          </form>
        </div>
      </section>
    </main>
  );
};

export default Index;
