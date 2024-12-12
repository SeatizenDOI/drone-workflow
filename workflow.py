from argparse import ArgumentParser, Namespace

from src.utils.parse_opt import get_list_sessions
from src.utils.SessionDrone import SessionDrone
from src.utils.GlobalMetadataGeoflow import GlobalMetadataGeoflow

def parse_args() -> Namespace:

    # Parse command line arguments.
    ap = ArgumentParser(description="Drone workflow", epilog="Thanks to use it!")

    # Input.
    arg_input = ap.add_mutually_exclusive_group(required=True)
    arg_input.add_argument("-efol", "--enable_folder", action="store_true", help="Take all images from a folder of a seatizen session")
    arg_input.add_argument("-eses", "--enable_session", action="store_true", help="Take all images from a single seatizen session")
    arg_input.add_argument("-ecsv", "--enable_csv", action="store_true", help="Take all images from session in csv file")

    # Path of input.
    ap.add_argument("-pfol", "--path_folder", default="/media/bioeos/E/drone_serge_test", help="Load all images from a folder of sessions")
    ap.add_argument("-pses", "--path_session", default="/home/bioeos/Documents/Bioeos/annotations_some_image/20240524_REU-LE-PORT_HUMAN-1_01/", help="Load all images from a single session")
    ap.add_argument("-pcsv", "--path_csv_file", default="./csv_inputs/stleu.csv", help="Load all images from session write in the provided csv file")

    # Optional arguments.
    ap.add_argument("-c", "--clean", action="store_true", help="Clean pdf preview and predictions files")
    ap.add_argument("-is", "--index_start", default="0", help="Choose from which index to start")
    ap.add_argument("-ip", "--index_position", default="-1", help="if != -1, take only session at selected index")
    
    # Geoflow arguments.
    ap.add_argument("-og", "--only_geoflow", action="store_true", help="Run only geoflow pipeline. If no ISO 19115 config file generated, nothing happen")
    ap.add_argument("-pgl", "--path_geoflow_library", default="/home/bioeos/R/x86_64-pc-linux-gnu-library/4.4/", help="Path to R library where geoflow package is")
    ap.add_argument("-icfg", "--input_config_file_geoflow", default="./configs/test_config.json", help="Static value to put in geoflow workflow")
    ap.add_argument("-pog", "--path_output_geoflow", default="./output", help="Where to store geoflow output and ISO 19115 config file")

    return ap.parse_args()


def main(opt: Namespace) -> None:

    # Stat.
    sessions_fail = []
    list_session = get_list_sessions(opt)
    index_start = int(opt.index_start) if opt.index_start.isnumeric() and int(opt.index_start) < len(list_session) else 0
    index_position = int(opt.index_position)-1 if opt.index_position.isnumeric() and \
                                            int(opt.index_position) > 0 and \
                                            int(opt.index_position) <= len(list_session) else -1
    sessions = list_session[index_start:] if index_position == -1 else [list_session[index_position]]
    print("\n-- Start drone workflow !", end="\n\n")

    # Setup global metadata to perform geoflow 
    metadata_geoflow = GlobalMetadataGeoflow(
        folder_to_save=opt.path_output_geoflow, 
        input_config_file_path=opt.input_config_file_geoflow, 
        session_parent_folder=str(sessions[0].parent) if len(sessions) > 0 else "",
        need_clean=opt.clean
    )




    if not opt.only_geoflow:
        # Iter on each session to setup 
        for session in sessions:
            print(f"\nLaunched session {session.name}\n\n")
            try:
                sessionDrone = SessionDrone(session)
                sessionDrone.generate_metadata(opt)

                metadata_geoflow.add_session(sessionDrone)

            except Exception as e:
                sessions_fail.append(session.name)
                print(e)

        metadata_geoflow.generate_config_json()
        metadata_geoflow.generate_metadata_geoflow()

    metadata_geoflow.launch_geoflow(opt.path_geoflow_library)
    metadata_geoflow.move_xml_files()

    # Stat.
    print("\nEnd of process. On {} sessions, {} fails. ".format(len(sessions), len(sessions_fail)))
    if (len(sessions_fail)):
        [print("\t* " + session_name) for session_name in sessions_fail]
        

if __name__ == "__main__":
    args = parse_args()
    main(args)