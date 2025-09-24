import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Mail } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class GlobalErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by GlobalErrorBoundary:', error, errorInfo);

    // You could send this error to an error reporting service
    // this.logErrorToService(error, errorInfo);
  }

  private logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    // Placeholder for error logging service
    console.group('Error Details:');
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
    console.error('Component Stack:', errorInfo.componentStack);
    console.groupEnd();
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleClearStorage = () => {
    try {
      localStorage.clear();
      sessionStorage.clear();
      window.location.reload();
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  };

  private renderErrorDetails() {
    const { error, errorInfo } = this.state;

    if (!error) return null;

    return (
      <details className="mt-4 p-4 bg-gray-50 rounded-lg">
        <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
          Technical Details
        </summary>
        <div className="mt-2 space-y-2">
          <div>
            <h4 className="text-xs font-semibold text-gray-600 uppercase">Error Message</h4>
            <p className="text-sm text-gray-800 font-mono">{error.message}</p>
          </div>
          {errorInfo && (
            <div>
              <h4 className="text-xs font-semibold text-gray-600 uppercase">Component Stack</h4>
              <pre className="text-xs text-gray-600 font-mono overflow-x-auto whitespace-pre-wrap">
                {errorInfo.componentStack}
              </pre>
            </div>
          )}
        </div>
      </details>
    );
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 space-y-4">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-red-100 rounded-full">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>

            <div className="text-center space-y-2">
              <h1 className="text-2xl font-bold text-gray-900">Oops! Something went wrong</h1>
              <p className="text-gray-600">
                We're sorry, but something unexpected happened. Don't worry, your data is safe.
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Reload Page
              </button>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={this.handleGoHome}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <Home className="w-4 h-4" />
                  Go Home
                </button>

                <button
                  onClick={this.handleClearStorage}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Clear Data
                </button>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <Mail className="w-4 h-4" />
                <span>Still having issues? Contact support</span>
              </div>
            </div>

            {process.env.NODE_ENV === 'development' && this.renderErrorDetails()}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}