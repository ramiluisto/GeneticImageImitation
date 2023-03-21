from src_numpy.evolution import Simulation


if __name__ == "NOT__main__":
    import os, json

    sim = Simulation(5)
    sim.iter_count = 0

    while sim.iter_count <= 5:
        print(f"\rDoing round {sim.iter_count:>9}...", end="")
        sim.do_one_round()
        if (sim.iter_count % 10) == 0:
            filebase = f"Run_{sim.iter_count:09d}"
            img_path = os.path.join("./runtestdata/img/", filebase + ".png")
            data_path = os.path.join("./runtestdata/data/", filebase + ".json")
            # print(f"\n\nSaving to img path {img_path}, json path {data_path}\n\n")
            sim.best_image().save(img_path)

            data = {canvas.code: score for canvas, score in sim.scored_canvases.items()}
            with open(data_path, "w") as fp:
                json.dump(data, fp)


if __name__ == "__main__":
    sim = Simulation()
    sim.run()
