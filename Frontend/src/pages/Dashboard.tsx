import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "next-themes";
import { Pencil, Trash2, FileDown, LogOut, Save, Moon, Sun, UserCircle, LayoutDashboard, Heart, BookOpen, Gift, MessageSquare, ListChecks } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import { toast } from "sonner";
import { Usuario, Antepassado } from "@/types";
import favicon from "@/assets/favicon.ico";
import logoDark from "@/assets/logo-texto-branco.png";
import logoLight from "@/assets/logo-texto-preto.png";

type Lineage = "Materna" | "Paterna" | "Não aplicável";
type Family = "Minha Família" | "Família do Cônjuge";

const BOND_OPTIONS = [
  "Tataravô",
  "Tataravó",
  "Bisavô",
  "Bisavó",
  "Avô",
  "Avó",
  "Pai",
  "Mãe",
  "Cônjuge",
  "Filho",
  "Filha",
  "Neto",
  "Neta",
  "Bisneto",
  "Bisneta",
  "Tio-avô",
  "Tia-avó",
  "Tio",
  "Tia",
  "Irmão",
  "Irmã",
  "Sobrinho",
  "Sobrinha",
  "Primo",
  "Prima",
  "Sogro",
  "Sogra",
  "Cunhado",
  "Cunhada",
  "Padrasto",
  "Madrasta",
  "Enteado",
  "Enteada",
  "Parente afim",
  "Amigo",
  "Amiga",
  "Outro",
];

const Dashboard = () => {
  const { theme, setTheme } = useTheme();
  const [user, setUser] = useState<Usuario | null>(null);
  const [editUser, setEditUser] = useState<Partial<Usuario>>({});
  const [spirit, setSpirit] = useState("");
  const [bond, setBond] = useState<string>("");
  const [lineage, setLineage] = useState<Lineage>("Paterna");
  const [family, setFamily] = useState<Family>("Minha Família");
  const [records, setRecords] = useState<Antepassado[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const navigate = useNavigate();

  const allowedAncestors = [
    "Tataravô", "Tataravó", "Bisavô", "Bisavó", "Avô", "Avó", 
    "Tio-avô", "Tia-avó", "Tio", "Tia", "Primo", "Prima"
  ];
  const canSelectLineage = allowedAncestors.includes(bond);

  const [isEditOpen, setIsEditOpen] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/");
      return;
    }
    const parsedUser = JSON.parse(storedUser);
    setUser(parsedUser);
    setEditUser(parsedUser);
    loadRecords(parsedUser.id);
  }, [navigate]);

  const loadRecords = async (userId: number) => {
    try {
      const data = await api.listAntepassados(userId);
      setRecords(data);
    } catch (error: any) {
      toast.error("Erro ao carregar registros: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    try {
      const updated = await api.updateUsuario(user.id, editUser);
      setUser(updated);
      localStorage.setItem("user", JSON.stringify(updated));
      setIsEditOpen(false);
      toast.success("Perfil atualizado!");
    } catch (error: any) {
      toast.error("Erro ao atualizar perfil: " + error.message);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!spirit.trim() || !bond || !user) {
        toast.error("Preencha o nome e o vínculo");
        return;
    }

    try {
      const newRecord = await api.createAntepassado({
        nome_completo: spirit.trim(),
        vinculo: bond,
        linhagem: lineage,
        familia: family,
        usuario_id: user.id
      });
      setRecords((prev) => [newRecord, ...prev]);
      setSpirit("");
      setBond("");
      setLineage("Paterna");
      setFamily("Minha Família");
      toast.success("Registro salvo!");
    } catch (error: any) {
      toast.error("Erro ao salvar: " + error.message);
    }
  };

  const handleDelete = async (id?: number) => {
    if (!id) return;
    try {
      await api.deleteAntepassado(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
      toast.success("Registro removido");
    } catch (error: any) {
      toast.error("Erro ao remover: " + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  const handleExportPDF = () => {
    if (!user) return;
    window.open(api.getExportUrl(user.id), "_blank");
  };

  // Atualiza valores quando o vínculo muda
  useEffect(() => {
    if (!canSelectLineage && !["Amigo", "Amiga", "Outro"].includes(bond)) {
      setLineage("Não aplicável");
    }
  }, [bond, canSelectLineage]);

  if (!user || !mounted) return null;

  const isDark = theme === "dark";
  const currentLogo = isDark ? logoDark : logoLight;

  const navItems = [
    { label: "Dashboard", icon: LayoutDashboard },
    { label: "Culto às Almas dos Antepassados", icon: BookOpen },
    { label: "Culto Natalício", icon: Heart },
    { label: "Culto Paraíso Terrestre", icon: Heart },
    { label: "Donativo", icon: Gift },
    { label: "Pedido de Prece", icon: MessageSquare },
    { label: "Sorei-Saishi", icon: ListChecks },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card p-6 flex flex-col flex-shrink-0">
        <div className="flex items-center gap-2 mb-8">
          <img src={favicon} alt="Logo" className="w-8 h-8" />
          <span className="font-bold text-lg">Messianica</span>
        </div>

        <nav className="flex-1 space-y-2 overflow-y-auto pr-2 custom-scrollbar mb-8">
          {navItems.map((item) => (
            <Button 
              key={item.label} 
              variant="ghost" 
              className="w-full justify-start gap-3 h-auto py-2 px-3 whitespace-normal text-left items-start"
            >
              <item.icon className="w-4 h-4 mt-1 flex-shrink-0" />
              <span className="leading-tight">{item.label}</span>
            </Button>
          ))}
        </nav>

        <div className="h-px bg-border mb-8" />

        <div className="space-y-4">
          <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full justify-start gap-3">
                <UserCircle className="w-4 h-4" />
                Perfil
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Editar Perfil</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="space-y-2">
                  <Label>Nome Real</Label>
                  <Input value={editUser.nome_real || ""} onChange={(e) => setEditUser({...editUser, nome_real: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Sobrenome</Label>
                  <Input value={editUser.sobrenome || ""} onChange={(e) => setEditUser({...editUser, sobrenome: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label>Igreja</Label>
                  <Select 
                    value={editUser.igreja || ""} 
                    onValueChange={(value) => setEditUser({...editUser, igreja: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione a Igreja" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Lisboa">Lisboa</SelectItem>
                      <SelectItem value="Guimarães">Guimarães</SelectItem>
                      <SelectItem value="Braga">Braga</SelectItem>
                      <SelectItem value="Porto">Porto</SelectItem>
                      <SelectItem value="Coimbra">Coimbra</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Tipo de Membro</Label>
                  <Select 
                    value={editUser.tipo_usuario || ""} 
                    onValueChange={(value) => setEditUser({...editUser, tipo_usuario: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Membro">Membro</SelectItem>
                      <SelectItem value="Frequentador">Frequentador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Estado Civil</Label>
                  <Select 
                    value={editUser.estado_civil || ""} 
                    onValueChange={(value) => setEditUser({...editUser, estado_civil: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o estado civil" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Viúvo(a)">Viúvo(a)</SelectItem>
                      <SelectItem value="Casado(a)">Casado(a)</SelectItem>
                      <SelectItem value="Separado(a)">Separado(a)</SelectItem>
                      <SelectItem value="Solteiro(a)">Solteiro(a)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full">Salvar Alterações</Button>
              </form>
            </DialogContent>
          </Dialog>
          <Button variant="ghost" className="w-full justify-start gap-3 text-destructive" onClick={handleLogout}>
            <LogOut className="w-4 h-4" />
            Sair
          </Button>
        </div>
      </aside>

      {/* Conteúdo Principal */}
      <main className="flex-1 p-8 overflow-y-auto relative">
        <header className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <div className="flex items-center gap-2">
                <Sun className="h-4 w-4" />
                <Switch checked={isDark} onCheckedChange={(c) => setTheme(c ? "dark" : "light")} />
                <Moon className="h-4 w-4" />
            </div>
        </header>

      <section className="relative z-10 mx-auto w-full max-w-6xl px-6 pt-6 pb-12">
        {/* Cabeçalho Unificado - Compacto */}
        <div className={cn(
          "mx-auto flex max-w-xl flex-col items-center text-center rounded-2xl border px-6 py-4 shadow-elegant backdrop-blur sm:px-8 sm:py-6 mb-10 transition-all duration-300",
          isDark 
            ? "border-white/10 bg-zinc-800/95 text-white" 
            : "border-zinc-200 bg-white text-zinc-900"
        )}>
          <img
            src={currentLogo}
            alt="Igreja Messiânica Mundial de Portugal"
            width={240}
            height={240}
            className="h-56 w-56 object-contain mb-2"
          />
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Registro de Antepassados
          </h1>
          <p className={cn(
            "mt-1 text-sm",
            isDark ? "text-zinc-100" : "text-zinc-600"
          )}>
            Adicione e organize os antepassados da sua família com cuidado e clareza.
          </p>
        </div>

        {/* Formulário - Branco no Claro, Cinza no Escuro */}
        <form
          onSubmit={handleSave}
          className={cn(
            "mx-auto mt-10 w-full max-w-xl space-y-5 rounded-2xl border p-6 shadow-elegant backdrop-blur sm:p-8 transition-all duration-300",
            isDark 
              ? "border-white/10 bg-zinc-800/95" 
              : "border-zinc-200 bg-white"
          )}
        >
          <div className="space-y-2">
            <Label
              htmlFor="spirit"
              className={cn("text-xs font-medium", isDark ? "text-white" : "text-zinc-700")}
            >
              Nome do Espírito
            </Label>
            <Input
              id="spirit"
              value={spirit}
              onChange={(e) => setSpirit(e.target.value)}
              placeholder="Ex.: Maria José"
              className={cn(
                "h-11 rounded-lg border-border bg-background text-sm placeholder:text-zinc-400 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/15",
                isDark && "text-white border-zinc-700"
              )}
            />
          </div>

          <div className="space-y-2">
            <Label className={cn("text-xs font-medium", isDark ? "text-white" : "text-zinc-700")}>
              Vínculo
            </Label>
            <Select value={bond} onValueChange={setBond}>
              <SelectTrigger className={cn("h-11 rounded-lg border-border bg-background text-sm focus:ring-2 focus:ring-primary/15", isDark && "text-white border-zinc-700")}>
                <SelectValue placeholder="Selecione o Vínculo" />
              </SelectTrigger>
              <SelectContent>
                {BOND_OPTIONS.map((b) => (
                  <SelectItem key={b} value={b}>
                    {b}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <fieldset className="space-y-3">
            <legend className={cn("text-xs font-medium", isDark ? "text-white" : "text-zinc-700")}>
              Linhagem
            </legend>
            <RadioGroup
              value={lineage}
              onValueChange={(v) => setLineage(v as Lineage)}
              className="grid grid-cols-1 gap-2 sm:grid-cols-3"
            >
              { (["Materna", "Paterna", "Não aplicável"] as Lineage[]).map((opt) => (
                <Label
                  key={opt}
                  htmlFor={`lineage-${opt}`}
                  className={cn(
                    "flex cursor-pointer items-center gap-2.5 rounded-lg border bg-background px-3.5 py-2.5 text-sm font-normal transition-smooth",
                    (!canSelectLineage && opt !== "Não aplicável") ? "opacity-50 cursor-not-allowed" : "hover:border-primary/40",
                    lineage === opt
                      ? "border-primary bg-primary/5 text-primary font-semibold"
                      : isDark ? "border-zinc-700 text-zinc-100" : "border-zinc-300 text-zinc-600"
                  )}
                >
                  <RadioGroupItem
                    id={`lineage-${opt}`}
                    value={opt}
                    disabled={!canSelectLineage && opt !== "Não aplicável"}
                    className="border-zinc-400 data-[state=checked]:border-primary"
                  />
                  {opt}
                </Label>
              ))}
              </RadioGroup>
              </fieldset>

              <fieldset className="space-y-3">
              <legend className={cn("text-xs font-medium", isDark ? "text-white" : "text-zinc-700")}>
              Pertence à
              </legend>
              <RadioGroup
              value={family}
              onValueChange={(v) => setFamily(v as Family)}
              className="grid grid-cols-1 gap-2 sm:grid-cols-2"
              >
              {(["Minha Família", "Família do Cônjuge"] as Family[]).map((opt) => (
                <Label
                  key={opt}
                  htmlFor={`family-${opt}`}
                  className={cn(
                    "flex cursor-pointer items-center gap-2.5 rounded-lg border bg-background px-3.5 py-2.5 text-sm font-normal transition-smooth",
                    !canSelectLineage ? "opacity-50 cursor-not-allowed" : "hover:border-primary/40",
                    family === opt
                      ? "border-primary bg-primary/5 text-primary font-semibold"
                      : isDark ? "border-zinc-700 text-zinc-100" : "border-zinc-300 text-zinc-600"
                  )}
                >
                  <RadioGroupItem
                    id={`family-${opt}`}
                    value={opt}
                    disabled={!canSelectLineage}
                    className="border-zinc-400 data-[state=checked]:border-primary"
                  />
                  {opt}
                </Label>
              ))}
              </RadioGroup>
          </fieldset>

          <Button
            type="submit"
            className="group h-11 w-full rounded-lg bg-primary text-sm font-medium text-primary-foreground shadow-soft transition-smooth hover:bg-[hsl(var(--primary-hover))] hover:shadow-elegant"
          >
            <Save className="mr-2 h-4 w-4" />
            Salvar Registro
          </Button>
        </form>
      </section>

        {/* Tabela de Registros - Cinza Neutro e Claro */}
        <section className="mt-14">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className={cn("text-lg font-semibold tracking-tight", isDark ? "text-white" : "text-zinc-900")}>
                Registos
              </h2>
              <p className={cn("text-xs", isDark ? "text-zinc-100" : "text-zinc-500")}>
                Total de registos: {records.length}
              </p>
            </div>
            <Button
              onClick={handleExportPDF}
              variant="outline"
              size="sm"
              className={cn(
                "h-9 gap-2 border-primary/30 text-primary hover:bg-primary/5 hover:text-primary",
                isDark && "border-primary/50 text-primary-foreground bg-primary/10"
              )}
            >
              <FileDown className="h-4 w-4" />
              Exportar PDF
            </Button>
          </div>

          <div className={cn(
            "overflow-hidden rounded-2xl border shadow-elegant backdrop-blur",
            isDark ? "border-white/10 bg-zinc-800/95" : "border-zinc-200 bg-white"
          )}>
            <Table>
              <TableHeader>
                <TableRow className="border-border/70 hover:bg-transparent">
                  <TableHead className={cn("text-xs font-medium uppercase tracking-wider", isDark ? "text-zinc-100" : "text-zinc-500")}>
                    Espírito
                  </TableHead>
                  <TableHead className={cn("text-xs font-medium uppercase tracking-wider", isDark ? "text-zinc-100" : "text-zinc-500")}>
                    Vínculo
                  </TableHead>
                  <TableHead className={cn("text-xs font-medium uppercase tracking-wider", isDark ? "text-zinc-100" : "text-zinc-500")}>
                    Linhagem
                  </TableHead>
                  <TableHead className={cn("text-xs font-medium uppercase tracking-wider", isDark ? "text-zinc-100" : "text-zinc-500")}>
                    Família
                  </TableHead>
                  <TableHead className={cn("w-[100px] text-right text-xs font-medium uppercase tracking-wider", isDark ? "text-zinc-100" : "text-zinc-500")}>
                    Ações
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-10 text-center">
                      Carregando...
                    </TableCell>
                  </TableRow>
                ) : records.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={5}
                      className={cn("py-10 text-center text-sm", isDark ? "text-white" : "text-zinc-500")}
                    >
                      Nenhum registo ainda. Adicione o primeiro acima.
                    </TableCell>
                  </TableRow>
                ) : (
                  records.map((r) => (
                    <TableRow
                      key={r.id}
                      className="border-zinc-200/50 dark:border-zinc-700/50 transition-smooth hover:bg-muted/40"
                    >
                      <TableCell className={cn("font-medium", isDark ? "text-white" : "text-zinc-900")}>
                        {r.nome_completo}
                      </TableCell>
                      <TableCell className={isDark ? "text-white" : "text-zinc-700"}>
                        {r.vinculo}
                      </TableCell>
                      <TableCell className={isDark ? "text-white" : "text-zinc-700"}>
                        {r.linhagem}
                      </TableCell>
                      <TableCell className={isDark ? "text-white" : "text-zinc-700"}>
                        {r.familia}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className={cn("h-8 w-8 hover:bg-primary/10 hover:text-primary", isDark ? "text-white" : "text-zinc-500")}
                            aria-label={`Editar ${r.nome_completo}`}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(r.id)}
                            className={cn("h-8 w-8 hover:bg-destructive/10 hover:text-destructive", isDark ? "text-white" : "text-zinc-500")}
                            aria-label={`Eliminar ${r.nome_completo}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
