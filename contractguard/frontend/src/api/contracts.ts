import { apiRequest } from "./client";
import {
  Contract,
  ContractVersion,
  Clause,
  KeyTerm,
  RiskAnalysis,
  ChatMessage,
  Citation,
} from "../types";

export async function getContracts(): Promise<Contract[]> {
  return apiRequest<Contract[]>("/contracts");
}

export async function getContract(contractId: string): Promise<{
  contract: Contract;
  versions: ContractVersion[];
  current_version_id: string;
}> {
  return apiRequest(`/contracts/${contractId}`);
}

export async function uploadContract(
  file: File,
  title: string,
  contractType: string,
  partyRole: string,
  jurisdiction: string
): Promise<Contract> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  formData.append("contract_type", contractType);
  formData.append("party_role", partyRole);
  formData.append("jurisdiction", jurisdiction);

  return apiRequest<Contract>("/contracts", {
    method: "POST",
    body: formData,
  });
}

export async function uploadVersion(contractId: string, file: File): Promise<ContractVersion> {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<ContractVersion>(`/contracts/${contractId}/versions`, {
    method: "POST",
    body: formData,
  });
}

export async function deleteContract(contractId: string): Promise<{ message: string }> {
  return apiRequest(`/contracts/${contractId}`, {
    method: "DELETE",
  });
}

export async function getVersionClauses(versionId: string): Promise<Clause[]> {
  return apiRequest<Clause[]>(`/versions/${versionId}/clauses`);
}

export async function getVersionKeyTerms(versionId: string): Promise<KeyTerm[]> {
  return apiRequest<KeyTerm[]>(`/versions/${versionId}/key-terms`);
}

export async function getVersionRisk(versionId: string): Promise<RiskAnalysis> {
  return apiRequest<RiskAnalysis>(`/versions/${versionId}/risk`);
}

export async function getRiskHistory(contractId: string): Promise<any[]> {
  return apiRequest<any[]>(`/contracts/${contractId}/risk-history`);
}

export async function askContractQuestion(
  versionId: string,
  question: string
): Promise<{
  answer: string;
  citations: Citation[];
  tokens: { in: number; out: number };
  seconds: number;
}> {
  return apiRequest(`/versions/${versionId}/chat`, {
    method: "POST",
    body: JSON.stringify({ question, top_k: 4 }),
  });
}
