import { AlertTriangle, RefreshCw } from "lucide-react";

type ErrorStateProps = {

  title?: string;

  message?: string;

  onRetry: () => void;

  isRetrying?: boolean;
};

export default function ErrorState({
  title = "Unable to load filming locations",
  message = "We couldn't retrieve movie data from the backend server. The data service may be temporarily unavailable.",
  onRetry,
  isRetrying = false,
}: ErrorStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-20 max-w-md mx-auto text-center space-y-4">
      <div className="p-5 rounded-2xl bg-red-950/40 border border-red-800/80 text-red-300 text-sm space-y-2 shadow-xl">
        <div className="flex items-center justify-center gap-2 text-red-400 font-semibold text-base">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{title}</span>
        </div>
        <p className="text-xs text-red-300/80 leading-relaxed">{message}</p>
      </div>

      <button
        type="button"
        onClick={onRetry}
        disabled={isRetrying}
        className="px-4 py-2.5 text-xs font-semibold rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isRetrying ? "animate-spin" : ""}`} />
        <span>{isRetrying ? "Retrying..." : "Try Again"}</span>
      </button>
    </div>
  );
}
