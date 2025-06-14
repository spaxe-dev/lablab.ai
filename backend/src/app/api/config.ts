// API Configuration
export const API_CONFIG = {
  services: {
    dependencyHealth: {
      baseUrl: process.env.DEPENDENCY_HEALTH_URL || 'http://localhost:8000',
      name: 'dependency-health'
    },
    autoTests: {
      baseUrl: process.env.AUTO_TESTS_URL || 'http://localhost:8001', 
      name: 'auto-tests'
    },
    prReview: {
      baseUrl: process.env.PR_REVIEW_URL || 'http://localhost:8002',
      name: 'pr-review'
    }
  },
  timeout: 30000, // 30 seconds
  retries: 3
};

// Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  details?: string;
}

export interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'error';
  port: number;
  available: boolean;
  error?: string;
}

export interface SystemStatus {
  success: boolean;
  backend_status: string;
  timestamp: string;
  services: {
    healthy: number;
    total: number;
    details: ServiceStatus[];
  };
  endpoints: Record<string, Record<string, string>>;
}

// Dependency Health Types
export interface DependencyHealthRequest {
  repo_url?: string;
  branch?: string;
  content?: string;
  file_type?: 'requirements.txt' | 'package.json';
}

export interface Vulnerability {
  cve_id: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN';
  published_date: string;
  affected_versions: string[];
  fixed_versions: string[];
}

export interface DependencyResult {
  dependency: {
    name: string;
    version: string;
    type: 'python' | 'node';
  };
  vulnerabilities: Vulnerability[];
  is_vulnerable: boolean;
  risk_level: string;
}

export interface DependencyHealthResponse {
  total_dependencies: number;
  vulnerable_dependencies: number;
  vulnerabilities_found: number;
  risk_summary: Record<string, number>;
  results: DependencyResult[];
  scan_timestamp: string;
}

// Auto Tests Types
export interface AutoTestsRequest {
  code: string;
  language?: 'python' | 'javascript' | 'typescript';
  test_type?: 'unit' | 'integration' | 'e2e';
}

// PR Review Types
export interface PRReviewRequest {
  pr_url?: string;
  code_diff?: string;
  repository?: string;
  review_type?: 'comprehensive' | 'security' | 'performance';
}
