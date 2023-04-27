import pymeshlab as ml
import os
import subprocess
import concurrent.futures
import threading
import subprocess
import time
from glyph_tables import typeball



PATH_TO_OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.com"




# Function to process each glyph
def process_glyph(case, row, column, glyph):
    if glyph == "":
        return
    filename = f"ballparts/{row}-{column}-{case}.STL"
    codepoints = [ord(x) for x in glyph]
    codepoints = str(codepoints).replace(" ", "")
    cmd = f"\"{PATH_TO_OPENSCAD}\" -o \"{filename}\" -D codepoints={codepoints} -D row={row} -D column={column} -D case={case} oneletter.scad"
    print(f"Generating glyph {glyph}...")
    subprocess.run(cmd)

    with lock:
        mainMeshSet.load_new_mesh(filename)
        #Need to fix 2 manifold edges
        #Repair non manifold edges by removing faces
        
        #Need to close holes
        
        mainMeshSet.generate_by_merging_visible_meshes()
        mainMeshSet.save_current_mesh("ballparts/textForTypeball.STL")
    print(f"Glyph {glyph} complete.")
    

    
if __name__ == "__main__":
    # Create the main mesh set that will contain the final ball
    mainMeshSet = ml.MeshSet()

    # Make a /ballparts folder to hold each individual glyph shape
    if not os.path.exists("ballparts"):
        os.mkdir("ballparts")

    # Initialize a ThreadPoolExecutor and a lock for synchronization
    executor = concurrent.futures.ThreadPoolExecutor()
    lock = threading.Lock()


    
    # Process each glyph in parallel using the executor
    futures = []
    if True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            for case, hemisphere in enumerate(typeball):
                for row, line in enumerate(hemisphere):
                    for column, glyph in enumerate(line):
                        print(f"Submitting {glyph}")
                        future = executor.submit(process_glyph, case, row, column, glyph)
                        futures.append(future)

            # Wait for all workers to finish, handling Ctrl-C
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("Interrupted! Canceling remaining tasks...")
                    for f in futures:
                        f.cancel()
                    exit()
    time.sleep(5) # Maybe this fixes it?
    # Once all glyphs are processed, put them onto the typeball body
    print("Attaching glyphs to typeball body...")
    mainMeshSet = ml.MeshSet() # Just reset the meshset, it's easier this way
    mainMeshSet.load_new_mesh("ballparts/textForTypeball.STL")
    #mainMeshSet.load_new_mesh(os.path.join("ballparts", "textForTypeball.STL"))
    mainMeshSet.load_new_mesh("typeball_blank.STL")
    #import pdb;pdb.set_trace()
    mainMeshSet.generate_boolean_union(first_mesh=0, second_mesh=1)
    mainMeshSet.save_current_mesh("typeball_finished.STL")
    print("Typeball finished!")