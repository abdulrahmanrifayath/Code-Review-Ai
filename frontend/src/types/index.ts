export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  role: 'ADMIN' | 'REVIEWER' | 'DEVELOPER'
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface Branch {
  name: string
  commit_sha: string
  protected: boolean
}

export interface Commit {
  id?: string
  commit_sha: string
  author_name?: string
  author_email?: string
  message: string
  created_at?: string
}

export interface PullRequest {
  id: string
  repository_id: string
  pr_number: number
  title: string
  body?: string
  state: 'open' | 'closed' | 'merged'
  head_branch: string
  base_branch: string
  head_sha: string
  author_login: string
  html_url?: string
  additions: number
  deletions: number
  changed_files_count: number
  created_at: string
}

export interface Repository {
  id: string
  name: string
  full_name: string
  owner_login: string
  default_branch: string
  is_private: boolean
  language?: string
  is_active: boolean
  created_at: string
}

export interface CodeReview {
  id: string
  repository_id: string
  pr_number: number
  commit_sha: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  summary?: string
  findings?: Record<string, unknown>
  metrics?: Record<string, unknown>
  created_at: string
}
