###################### Pupil-DLC Pipeline#########################

#!/usr/bin/env python
import os
import sys
import shutil
import click
import pyfiglet
import pandas as pd
import deeplabcut
from ellipse import ellipse_fitting
import time


sys.path.append(r"C:\Users\Valyria\Projects\Allen\Pupil_Tracking_Project\Scripts\yaml")
from yaml_section import replace_yaml_section

def analyze_and_ellipse(experiment, video_path, config_path):
    """Common: analyze video, fit ellipse, save CSV."""
    click.echo("→ running analysis & labeled video…")
    deeplabcut.analyze_videos(config_path, [video_path], save_as_csv=True)
    deeplabcut.create_labeled_video(config_path, [video_path], save_frames=False)
    click.echo("→ analysis done.")

    viddir = os.path.dirname(video_path)
    csv_file = next(f for f in os.listdir(viddir) if f.endswith(".csv"))
    df = pd.read_csv(os.path.join(viddir, csv_file), low_memory=False)

    t0 = time.time()
    ell_df = ellipse_fitting(df)
    click.echo(f"→ ellipse fitting took {time.time()-t0:.1f}s")

    # compute diameter
    y1 = df.iloc[2:, -5].astype(float)
    y0 = df.iloc[2:, -11].astype(float)
    x1 = df.iloc[2:, -6].astype(float)
    x0 = df.iloc[2:, -12].astype(float)
    euc = ((y1-y0)**2 + (x1-x0)**2).pow(0.5)
    euc.index = ell_df.index
    ell_df['Eye_Diameter'] = euc

    outpath = os.path.join(viddir, f"PupilEye_{experiment}.csv")
    ell_df.to_csv(outpath, index=False)
    click.secho(f"→ ellipse CSV saved: {outpath}", fg="green")

@click.command()
def main():
    click.clear()
    click.secho(pyfiglet.figlet_format("Pupil-DLC", font="slant"), fg="cyan")

    # choose path
    mode = click.prompt(
        "Model? [IM=Individual, GM=General]", 
        type=click.Choice(["IM","GM"]), default="GM"
    )

    experiment = click.prompt("Experiment name", type=str)
    video_path = click.prompt(
        "Full path to your video file", 
        type=click.Path(exists=True, dir_okay=False)
    )

    if mode == "IM":
        # create a fresh project
        config_path = deeplabcut.create_new_project(
            experiment, "You", [video_path],
            working_directory=os.getcwd(),
            copy_videos=True, multianimal=False
        )
        click.echo(f"→ project created: {config_path}")
        replace_yaml_section(config_path)

        # loop: label → ask to proceed
        while True:
            deeplabcut.extract_frames(config_path, mode="manual")
            deeplabcut.label_frames(config_path)
            if click.confirm("Proceed to training?"):
                break

        deeplabcut.check_labels(config_path, visualizeindividuals=True)
        deeplabcut.create_training_dataset(config_path, augmenter_type='imgaug')
        deeplabcut.train_network(
            config_path, shuffle=1, trainingsetindex=0,
            gputouse=0, max_snapshots_to_keep=5,
            autotune=False, displayiters=100,
            saveiters=15000, maxiters=100000, allow_growth=True
        )
        deeplabcut.evaluate_network(config_path, Shuffles=[1], plotting=True)

    else:  # mode == "GM"
        # user already has a config.yaml
        config_path = click.prompt(
            "Full path to your existing config file",
            type=click.Path(exists=True, dir_okay=False)
        )
        click.echo(f"→ using config: {config_path}")
        # (any GM-specific prep you already have…)

    # both IM & GM converge here:
    analyze_and_ellipse(experiment, video_path, config_path)

if __name__ == '__main__':
    main()
