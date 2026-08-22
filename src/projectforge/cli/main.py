import os
import sys
import json
import click
from pathlib import Path

from projectforge.config import settings as get_settings
from projectforge.models import ProjectContext, ProjectType, AcademicLevel, SkillResult
from projectforge.ai import get_provider
from projectforge.skills.registry import SkillRegistry
from projectforge.errors import ProjectForgeError, ConfigurationError

@click.group()
def cli():
    """ProjectForge: AI-powered project blueprints."""
    pass

@cli.command()
def init():
    """Initialize a new ProjectForge workspace."""
    click.echo("Initializing ProjectForge workspace...")
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("GEMINI_API_KEY=\n")
        click.secho("Created .env file. Please add your GEMINI_API_KEY.", fg="green")
    else:
        click.secho(".env already exists.", fg="yellow")
    
    if not os.path.exists("project_context.json"):
        ctx = ProjectContext(
            project_title="My Awesome App",
            project_description="A descriptive summary goes here (min 20 chars).",
            project_type=ProjectType.web_app
        )
        with open("project_context.json", "w") as f:
            f.write(ctx.model_dump_json(indent=2))
        click.secho("Created project_context.json template.", fg="green")
    else:
        click.secho("project_context.json already exists.", fg="yellow")

@cli.command()
@click.option("--context-file", default="project_context.json", type=click.Path(exists=True), help="Path to project context JSON.")
@click.option("--output-dir", default="blueprint", type=click.Path(), help="Directory to save generated blueprints.")
@click.argument("skills", nargs=-1)
def run(context_file, output_dir, skills):
    """Run specified skills (or 'all')."""
    try:
        settings = get_settings()
        ai_provider = get_provider(settings)
    except ConfigurationError as e:
        click.secho(f"Configuration Error: {e}", fg="red")
        sys.exit(1)

    try:
        with open(context_file, "r") as f:
            data = json.load(f)
            context = ProjectContext(**data)
    except Exception as e:
        click.secho(f"Error loading context: {e}", fg="red")
        sys.exit(1)

    if not skills:
        skills = ("all",)

    try:
        execution_order = SkillRegistry.get_execution_order(list(skills))
    except ProjectForgeError as e:
        click.secho(f"Error resolving skills: {e}", fg="red")
        sys.exit(1)

    click.echo(f"Execution order: {', '.join(execution_order)}")

    os.makedirs(output_dir, exist_ok=True)
    
    # Load previously generated skills from output directory
    upstream_results = {}
    
    for skill_name in execution_order:
        skill_class = SkillRegistry.get_skill(skill_name)
        skill_instance = skill_class()
        
        click.secho(f"\n--- Running {skill_instance.display_name} ---", fg="cyan")
        
        # Check if output already exists (basic caching)
        output_file = os.path.join(output_dir, f"{skill_name}.json")
        
        try:
            result = skill_instance.execute(context, upstream_results, ai_provider)
            upstream_results[skill_name] = result
            
            with open(output_file, "w") as f:
                f.write(result.model_dump_json(indent=2))
                
            click.secho(f"Success! Saved to {output_file}", fg="green")
            
        except ProjectForgeError as e:
            click.secho(f"Error executing {skill_name}: {e}", fg="red")
            sys.exit(1)
            
    click.secho("\nAll requested skills completed successfully!", fg="green", bold=True)

if __name__ == "__main__":
    cli()
