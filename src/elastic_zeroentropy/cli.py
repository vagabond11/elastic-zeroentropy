"""
Command-line interface for elastic-zeroentropy library.

This module provides a CLI for performing searches, health checks,
and configuration management.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.json import JSON

from .config import ElasticZeroEntropyConfig, load_config
from .reranker import ElasticZeroEntropyReranker
from .exceptions import ElasticZeroEntropyError
from .models import RerankerConfig

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--config", type=click.Path(exists=True), help="Path to configuration file"
)
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str]) -> None:
    """
    Elastic-ZeroEntropy: Intelligent search with Elasticsearch and ZeroEntropy reranking.

    A command-line tool for performing searches with automatic reranking
    using ZeroEntropy's state-of-the-art models.
    """
    setup_logging(debug)

    # Load configuration
    try:
        if config:
            ctx.obj = load_config(env_file=config)
        else:
            ctx.obj = load_config()
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("query", required=True)
@click.argument("index", required=True)
@click.option("--top-k", type=int, default=10, help="Number of results to return")
@click.option(
    "--top-k-initial",
    type=int,
    default=100,
    help="Number of documents to retrieve from Elasticsearch",
)
@click.option(
    "--top-k-rerank",
    type=int,
    default=20,
    help="Number of documents to send for reranking",
)
@click.option("--model", default="zerank-1", help="ZeroEntropy model to use")
@click.option("--no-rerank", is_flag=True, help="Disable reranking")
@click.option("--filters", help="JSON string of additional filters")
@click.option(
    "--output",
    type=click.Choice(["table", "json", "simple"]),
    default="table",
    help="Output format",
)
@click.option("--debug-info", is_flag=True, help="Include debug information in output")
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    index: str,
    top_k: int,
    top_k_initial: int,
    top_k_rerank: int,
    model: str,
    no_rerank: bool,
    filters: Optional[str],
    output: str,
    debug_info: bool,
) -> None:
    """
    Perform a search query with optional reranking.

    QUERY: The search query text
    INDEX: The Elasticsearch index to search
    """
    config: ElasticZeroEntropyConfig = ctx.obj

    # Parse filters if provided
    parsed_filters = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in filters: {e}[/red]")
            sys.exit(1)

    # Create reranker config
    reranker_config = RerankerConfig(
        top_k_initial=top_k_initial,
        top_k_rerank=top_k_rerank,
        top_k_final=top_k,
        model=model,
        combine_scores=True,
        score_weights={"elasticsearch": 0.3, "rerank": 0.7},
    )

    async def run_search() -> None:
        """Run the search operation."""
        try:
            async with ElasticZeroEntropyReranker(config) as reranker:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("Searching...", total=None)

                    response = await reranker.search(
                        query=query,
                        index=index,
                        reranker_config=reranker_config,
                        filters=parsed_filters,
                        enable_reranking=not no_rerank,
                        return_debug_info=debug_info,
                    )

                    progress.remove_task(task)

                # Display results
                display_search_results(response, output)

        except ElasticZeroEntropyError as e:
            console.print(f"[red]Search failed: {e.message}[/red]")
            if debug_info and e.details:
                console.print(
                    f"[yellow]Details: {json.dumps(e.details, indent=2)}[/yellow]"
                )
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)

    asyncio.run(run_search())


def display_search_results(response: Any, output_format: str) -> None:
    """Display search results in the specified format."""
    if output_format == "json":
        # Convert to JSON-serializable format
        result_dict = {
            "query": response.query,
            "total_hits": response.total_hits,
            "took_ms": response.took_ms,
            "elasticsearch_took_ms": response.elasticsearch_took_ms,
            "reranking_took_ms": response.reranking_took_ms,
            "model_used": response.model_used,
            "reranking_enabled": response.reranking_enabled,
            "results": [],
        }

        for result in response.results:
            result_dict["results"].append(
                {
                    "rank": result.rank,
                    "score": result.score,
                    "elasticsearch_score": result.elasticsearch_score,
                    "rerank_score": result.rerank_score,
                    "document": {
                        "id": result.document.id,
                        "title": result.document.title,
                        "text": (
                            result.document.text[:200] + "..."
                            if len(result.document.text) > 200
                            else result.document.text
                        ),
                        "metadata": result.document.metadata,
                    },
                }
            )

        if response.debug_info:
            result_dict["debug_info"] = response.debug_info

        console.print(JSON(json.dumps(result_dict, indent=2)))

    elif output_format == "simple":
        console.print(f"Query: {response.query}")
        console.print(f"Found {response.total_hits} total hits in {response.took_ms}ms")
        console.print()

        for result in response.results:
            console.print(
                f"[bold]{result.rank}.[/bold] [green]{result.document.title or result.document.id}[/green]"
            )
            console.print(f"   Score: {result.score:.4f}")
            console.print(f"   {result.document.text[:150]}...")
            console.print()

    else:  # table format
        # Create summary panel
        summary_text = (
            f"Query: {response.query}\n"
            f"Total hits: {response.total_hits:,}\n"
            f"Total time: {response.took_ms}ms\n"
            f"Elasticsearch time: {response.elasticsearch_took_ms}ms\n"
        )

        if response.reranking_enabled and response.reranking_took_ms:
            summary_text += f"Reranking time: {response.reranking_took_ms}ms\n"
            summary_text += f"Model used: {response.model_used}\n"
        else:
            summary_text += "Reranking: Disabled\n"

        console.print(Panel(summary_text, title="Search Summary", expand=False))
        console.print()

        # Create results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Title/ID", style="green", min_width=20)
        table.add_column("Text Preview", style="dim", min_width=40)

        if response.reranking_enabled:
            table.add_column("ES Score", justify="right", width=8)
            table.add_column("Rerank", justify="right", width=8)

        for result in response.results:
            text_preview = (
                result.document.text[:100] + "..."
                if len(result.document.text) > 100
                else result.document.text
            )
            text_preview = text_preview.replace("\n", " ").replace("\r", " ")

            row = [
                str(result.rank),
                f"{result.score:.4f}",
                result.document.title or result.document.id[:20],
                text_preview,
            ]

            if response.reranking_enabled:
                es_score = (
                    f"{result.elasticsearch_score:.4f}"
                    if result.elasticsearch_score is not None
                    else "N/A"
                )
                rerank_score = (
                    f"{result.rerank_score:.4f}"
                    if result.rerank_score is not None
                    else "N/A"
                )
                row.extend([es_score, rerank_score])

            table.add_row(*row)

        console.print(table)

        # Debug info
        if response.debug_info:
            console.print()
            console.print(
                Panel(
                    JSON(json.dumps(response.debug_info, indent=2)),
                    title="Debug Information",
                )
            )


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check the health of Elasticsearch and ZeroEntropy connections."""
    config: ElasticZeroEntropyConfig = ctx.obj

    async def run_health_check() -> None:
        """Run the health check."""
        try:
            async with ElasticZeroEntropyReranker(config) as reranker:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("Checking health...", total=None)

                    health_response = await reranker.health_check()

                    progress.remove_task(task)

                # Display health status
                display_health_status(health_response)

        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
            sys.exit(1)

    asyncio.run(run_health_check())


def display_health_status(health_response: Any) -> None:
    """Display health check results."""
    # Overall status
    status_color = "green" if health_response.status == "healthy" else "red"
    console.print(
        f"Overall Status: [{status_color}]{health_response.status.upper()}[/{status_color}]"
    )
    console.print()

    # Elasticsearch status
    es_status = health_response.elasticsearch["status"]
    es_color = "green" if es_status == "healthy" else "red"

    es_panel_content = f"Status: [{es_color}]{es_status.upper()}[/{es_color}]\n"

    if "cluster_health" in health_response.elasticsearch:
        cluster_health = health_response.elasticsearch["cluster_health"]
        es_panel_content += (
            f"Cluster Status: {cluster_health.get('status', 'unknown')}\n"
        )
        es_panel_content += (
            f"Number of Nodes: {cluster_health.get('number_of_nodes', 'unknown')}\n"
        )

    if "elasticsearch_version" in health_response.elasticsearch:
        es_panel_content += (
            f"Version: {health_response.elasticsearch['elasticsearch_version']}\n"
        )

    if "error" in health_response.elasticsearch:
        es_panel_content += f"Error: {health_response.elasticsearch['error']}\n"

    console.print(Panel(es_panel_content, title="Elasticsearch", expand=False))

    # ZeroEntropy status
    ze_status = health_response.zeroentropy["status"]
    ze_color = "green" if ze_status == "healthy" else "red"

    ze_panel_content = f"Status: [{ze_color}]{ze_status.upper()}[/{ze_color}]\n"

    if "error" in health_response.zeroentropy:
        ze_panel_content += f"Error: {health_response.zeroentropy['error']}\n"
    else:
        ze_panel_content += "API connection successful\n"

    console.print(Panel(ze_panel_content, title="ZeroEntropy API", expand=False))

    # Version info
    console.print(f"Library Version: {health_response.version}")


@cli.command()
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Display current configuration."""
    config: ElasticZeroEntropyConfig = ctx.obj

    # Create configuration display (mask sensitive data)
    config_dict = config.dict()

    # Mask sensitive information
    if config_dict.get("zeroentropy_api_key"):
        config_dict["zeroentropy_api_key"] = (
            "*" * 8 + config_dict["zeroentropy_api_key"][-4:]
        )
    if config_dict.get("elasticsearch_password"):
        config_dict["elasticsearch_password"] = "*" * 8
    if config_dict.get("elasticsearch_api_key"):
        config_dict["elasticsearch_api_key"] = (
            "*" * 8 + config_dict["elasticsearch_api_key"][-4:]
        )

    console.print(
        Panel(JSON(json.dumps(config_dict, indent=2)), title="Current Configuration")
    )


@cli.command()
def config_template() -> None:
    """Generate a template .env file."""
    template = """# ZeroEntropy API Configuration
ZEROENTROPY_API_KEY=your_zeroentropy_api_key_here
ZEROENTROPY_BASE_URL=https://api.zeroentropy.dev/v1
ZEROENTROPY_MODEL=zerank-1
ZEROENTROPY_TIMEOUT=30.0
ZEROENTROPY_MAX_RETRIES=3

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_API_KEY=
ELASTICSEARCH_VERIFY_CERTS=true
ELASTICSEARCH_TIMEOUT=30.0

# Search Configuration
DEFAULT_TOP_K_INITIAL=100
DEFAULT_TOP_K_RERANK=20
DEFAULT_TOP_K_FINAL=10
DEFAULT_COMBINE_SCORES=true
DEFAULT_ELASTICSEARCH_WEIGHT=0.3
DEFAULT_RERANK_WEIGHT=0.7

# Logging Configuration
LOG_LEVEL=INFO
DEBUG=false
ENABLE_REQUEST_LOGGING=false

# Performance Configuration
MAX_CONCURRENT_REQUESTS=10
CONNECTION_POOL_SIZE=20
ENABLE_RATE_LIMITING=true
REQUESTS_PER_MINUTE=1000
"""

    env_file = Path(".env.example")
    env_file.write_text(template)

    console.print(f"[green]Template configuration written to {env_file}[/green]")
    console.print("Copy to .env and fill in your actual values.")


@cli.command()
@click.argument("index", required=True)
@click.option("--limit", type=int, default=5, help="Number of sample documents to show")
@click.pass_context
def inspect(ctx: click.Context, index: str, limit: int) -> None:
    """Inspect an Elasticsearch index structure and sample documents."""
    config: ElasticZeroEntropyConfig = ctx.obj

    async def run_inspect() -> None:
        """Run the index inspection."""
        try:
            from .elasticsearch_client import ElasticsearchClient

            async with ElasticsearchClient(config) as es_client:
                # Check if index exists
                if not await es_client.index_exists(index):
                    console.print(f"[red]Index '{index}' does not exist[/red]")
                    return

                # Get mapping
                mapping = await es_client.get_index_mapping(index)

                # Get sample documents
                sample_response = await es_client.search(
                    index=index, query={"match_all": {}}, size=limit
                )

                # Display mapping
                console.print(
                    Panel(
                        JSON(json.dumps(mapping, indent=2)),
                        title=f"Index Mapping: {index}",
                    )
                )

                # Display sample documents
                if sample_response.documents:
                    console.print()
                    console.print(
                        f"[bold]Sample Documents ({len(sample_response.documents)}):[/bold]"
                    )

                    for i, doc in enumerate(sample_response.documents, 1):
                        console.print(f"\n[green]Document {i}:[/green]")
                        console.print(f"  ID: {doc.id}")
                        console.print(f"  Title: {doc.title or 'N/A'}")
                        console.print(f"  Text: {doc.text[:200]}...")
                        if doc.metadata:
                            console.print(
                                f"  Metadata: {json.dumps(doc.metadata, indent=2)}"
                            )
                else:
                    console.print(
                        f"[yellow]No documents found in index '{index}'[/yellow]"
                    )

        except Exception as e:
            console.print(f"[red]Inspection failed: {e}[/red]")
            sys.exit(1)

    asyncio.run(run_inspect())


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
