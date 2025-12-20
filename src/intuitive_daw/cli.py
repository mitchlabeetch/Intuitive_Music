"""Command-line interface for the DAW"""
import click
import os
import yaml
from pathlib import Path

from ..api.server import DAWServer
from ..core.project import Project
from ..core.engine import AudioEngine


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Intuitive Music DAW - AI-Assisted Digital Audio Workstation"""
    pass


@main.command()
@click.option('--host', default='127.0.0.1', help='Server host')
@click.option('--port', default=5000, help='Server port')
@click.option('--debug/--no-debug', default=True, help='Debug mode')
@click.option('--config', type=click.Path(exists=True), help='Config file path')
def serve(host, port, debug, config):
    """Start the DAW server"""
    
    # Load configuration
    config_data = {}
    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
    
    # Create and run server
    server = DAWServer(config_data)
    server.run(host=host, port=port, debug=debug)


@main.command()
@click.argument('name')
@click.option('--path', default=None, help='Project directory path')
def create(name, path):
    """Create a new project"""
    project_path = path or f'./projects/{name}'
    
    project = Project(name=name, path=project_path)
    
    if project.save():
        click.echo(f"✓ Created project '{name}' at {project_path}")
    else:
        click.echo(f"✗ Failed to create project", err=True)


@main.command()
@click.argument('path', type=click.Path(exists=True))
def info(path):
    """Show project information"""
    project = Project.load(path)
    
    if project:
        click.echo(f"\nProject: {project.metadata.name}")
        click.echo(f"Created: {project.metadata.created_at}")
        click.echo(f"Modified: {project.metadata.modified_at}")
        click.echo(f"Tempo: {project.metadata.tempo} BPM")
        click.echo(f"Time Signature: {project.metadata.time_signature[0]}/{project.metadata.time_signature[1]}")
        click.echo(f"Key: {project.metadata.key}")
        click.echo(f"Tracks: {len(project.tracks)}")
        click.echo(f"Markers: {len(project.markers)}")
    else:
        click.echo(f"✗ Failed to load project from {path}", err=True)


@main.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('output_path')
@click.option('--format', default='wav', help='Output format')
@click.option('--duration', default=None, type=float, help='Duration in seconds')
def export(project_path, output_path, format, duration):
    """Export project to audio file"""
    project = Project.load(project_path)
    
    if not project:
        click.echo(f"✗ Failed to load project", err=True)
        return
    
    # Determine duration
    export_duration = duration or project.get_duration()
    
    if export_duration == 0:
        click.echo("✗ Project has no duration", err=True)
        return
    
    click.echo(f"Exporting {project.metadata.name} to {output_path}...")
    
    # Initialize audio engine
    engine = AudioEngine()
    engine.initialize()
    
    # Add tracks to engine
    for track in project.tracks:
        engine.add_track(track)
    
    # Render
    success = engine.render(output_path, export_duration)
    
    if success:
        click.echo(f"✓ Successfully exported to {output_path}")
    else:
        click.echo(f"✗ Export failed", err=True)


@main.command()
def init():
    """Initialize DAW environment"""
    click.echo("Initializing Intuitive Music DAW...")
    
    # Create necessary directories
    directories = [
        './projects',
        './plugins',
        './temp_audio',
        './render_output'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        click.echo(f"✓ Created {directory}")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("# Intuitive Music DAW Configuration\n")
            f.write("FLASK_ENV=development\n")
            f.write("SECRET_KEY=change-me-in-production\n")
            f.write("OPENAI_API_KEY=\n")
        click.echo("✓ Created .env file")
    
    click.echo("\n✓ Initialization complete!")
    click.echo("\nNext steps:")
    click.echo("1. Edit .env file and add your API keys")
    click.echo("2. Run 'intuitive-daw serve' to start the server")
    click.echo("3. Open your browser to http://localhost:5000")


@main.command()
def test():
    """Run system tests"""
    click.echo("Running system tests...")
    
    # Test audio engine
    click.echo("\nTesting audio engine...")
    engine = AudioEngine()
    if engine.initialize():
        click.echo("✓ Audio engine initialized")
    else:
        click.echo("✗ Audio engine initialization failed", err=True)
    
    # Test project creation
    click.echo("\nTesting project creation...")
    test_project = Project("Test Project", "/tmp/test_project")
    if test_project.save():
        click.echo("✓ Project creation works")
    else:
        click.echo("✗ Project creation failed", err=True)
    
    click.echo("\n✓ Tests complete!")


if __name__ == '__main__':
    main()
