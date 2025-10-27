import React from 'react'

type State = { hasError: boolean; error?: Error }

export default class ErrorBoundary extends React.Component<React.PropsWithChildren<{}>, State> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: any) {
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-50 text-red-900 rounded max-w-2xl mx-auto mt-6">
          <h3 className="text-lg font-semibold mb-2">Se produjo un error en este componente</h3>
          <pre className="text-xs whitespace-pre-wrap">{this.state.error?.message}</pre>
          <div className="mt-3 text-sm text-gray-700">Revisa la consola para más detalles.</div>
        </div>
      )
    }
    return this.props.children
  }
}
