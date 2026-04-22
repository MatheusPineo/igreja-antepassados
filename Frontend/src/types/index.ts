
export interface Usuario {
  id: number;
  nome_completo: string;
  email: string;
  google_id?: string;
  nome_real?: string;
  sobrenome?: string;
  igreja?: string;
  tipo_usuario?: string;
  foto?: string;
  estado_civil?: string;
  sexo?: string;
}

export interface Antepassado {
  id?: number;
  nome_completo: string;
  vinculo: string;
  linhagem: string;
  familia: string;
  usuario_id: number;
}
