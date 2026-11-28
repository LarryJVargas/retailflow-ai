import React from 'react';
import { Sparkles, ShieldCheck, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { InventoryAnalysisResponse } from '../../types/ai';
import { PriorityBadge, Badge } from '../common/Badge';
import { Button } from '../common/Button';

interface AiAnalysisPanelProps {
  analysis: InventoryAnalysisResponse | null;
  loading: boolean;
  onRunAnalysis: () => void;
  error?: string | null;
}

export const AiAnalysisPanel: React.FC<AiAnalysisPanelProps> = ({
  analysis,
  loading,
  onRunAnalysis,
  error,
}) => {
  return (
    <div className="space-y-6">
      {/* Cabecera del Panel */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <div className="p-1.5 rounded-lg bg-amber-100 text-amber-800 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Análisis Asistido de Inventario
            </h2>
            {analysis && (
              <Badge variant={analysis.source === 'gemini' ? 'gemini' : 'fallback'}>
                {analysis.source === 'gemini'
                  ? `Gemini AI (${analysis.model_used || 'gemini-3.5-flash'})`
                  : 'Motor Determinista (Fallback)'}
              </Badge>
            )}
          </div>
          <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
            Evalúa artículos en situación crítica para sintetizar diagnósticos y jerarquizar prioridades de reposición.
            <strong> Principio de seguridad:</strong> las cantidades de reposición son fijadas por el backend y verificadas contra alucinaciones.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={onRunAnalysis}
          loading={loading}
          icon={<RefreshCw className="w-4 h-4" />}
          className="w-full md:w-auto shrink-0"
        >
          {analysis ? 'Re-analizar Inventario' : 'Ejecutar Análisis'}
        </Button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Ocurrió un inconveniente al consultar el análisis</p>
            <p className="text-xs text-rose-700 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Tarjeta de Resumen Ejecutivo */}
      {analysis && (
        <div
          className={`rounded-xl border p-5 shadow-sm transition-all ${
            analysis.source === 'gemini'
              ? 'bg-gradient-to-br from-purple-50/70 via-white to-slate-50 border-purple-200'
              : 'bg-slate-50/80 border-slate-200'
          }`}
        >
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <ShieldCheck
                className={`w-5 h-5 ${
                  analysis.source === 'gemini' ? 'text-purple-600' : 'text-slate-600'
                }`}
              />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Resumen Ejecutivo
              </span>
            </div>
            <span className="text-xs text-slate-500 font-medium">
              {analysis.total_critical_products} producto(s) crítico(s)
            </span>
          </div>

          <p className="text-sm font-medium text-slate-800 leading-relaxed mb-3">
            "{analysis.summary}"
          </p>

          <div className="text-[11px] text-slate-500 flex items-center gap-1.5 pt-2 border-t border-slate-200/60">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span>
              {analysis.source === 'gemini'
                ? 'Análisis semántico generado mediante Google Gemini y validado por reglas de negocio.'
                : 'Respuesta generada mediante el motor local determinista ante indisponibilidad de API.'}
            </span>
          </div>
        </div>
      )}

      {/* Grid de Recomendaciones */}
      {analysis && analysis.recommendations.length > 0 && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Recomendaciones Priorizadas
            </h3>
            <span className="text-xs text-slate-500">
              Ordenado por nivel de urgencia
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysis.recommendations.map((rec) => (
              <div
                key={rec.sku}
                className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                      {rec.sku}
                    </span>
                    <PriorityBadge priority={rec.priority} />
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed mb-3">
                    {rec.explanation}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <span className="text-slate-500 font-medium">Cantidad a reponer (Backend):</span>
                  <span className="font-bold text-retail-700 text-sm">
                    +{rec.suggested_quantity} u.
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estado vacío si no se ejecutó análisis aún */}
      {!analysis && !loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-12 text-center text-slate-400 shadow-sm">
          <Sparkles className="w-10 h-10 text-amber-400/80 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-700 mb-1">
            Ningún análisis ejecutado en esta sesión
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mb-4">
            Presiona el botón para consultar a Gemini API y clasificar los productos con riesgo de quiebre de stock.
          </p>
          <Button variant="primary" size="sm" onClick={onRunAnalysis}>
            Iniciar Análisis Ahora
          </Button>
        </div>
      )}
    </div>
  );
};
