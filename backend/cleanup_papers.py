from services.mongodb import (
    papers_collection,
    shares_collection,
)

from services.backblaze import get_bucket


def main():
    print("=" * 60)
    print("SECURE QUESTION PAPER CLEANUP")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. GET ALL PAPERS
    # ---------------------------------------------------------

    papers = list(
        papers_collection.find(
            {},
            {
                "_id": 1,
                "paper_id": 1,
                "encrypted_object": 1,
            }
        )
    )

    print(f"\nQuestion papers found: {len(papers)}")

    if not papers:
        print("\nNothing to delete.")
        return

    print("\nPapers that will be deleted:")

    for paper in papers:
        print(
            f"  - {paper.get('paper_id', 'UNKNOWN')}"
        )

    # ---------------------------------------------------------
    # 2. CONFIRMATION
    # ---------------------------------------------------------

    print("\nWARNING:")
    print(
        "This will permanently delete all question-paper "
        "files and Shamir shares."
    )
    print(
        "Users and audit logs will NOT be deleted."
    )

    confirmation = input(
        "\nType DELETE to continue: "
    ).strip()

    if confirmation != "DELETE":
        print("\nCleanup cancelled.")
        return

    # ---------------------------------------------------------
    # 3. CONNECT TO BACKBLAZE
    # ---------------------------------------------------------

    print("\nConnecting to Backblaze B2...")

    bucket = get_bucket()

    print(
        f"Connected to bucket: {bucket.name}"
    )

    # ---------------------------------------------------------
    # 4. DELETE BACKBLAZE FILES
    # ---------------------------------------------------------

    deleted_b2 = 0
    failed_b2 = 0

    print("\nDeleting Backblaze files...")

    for paper in papers:
        paper_id = paper.get("paper_id")

        if not paper_id:
            print(
                "  ! Skipping record without paper_id"
            )
            continue

        # -----------------------------------------------------
        # Find every B2 object belonging to this paper
        # -----------------------------------------------------

        try:
            files = bucket.ls(
                folder_to_list=f"papers/{paper_id}",
                recursive=True,
                fetch_count=1000,
            )

            for file_version, _ in files:
                try:
                    bucket.delete_file_version(
                        file_version.id_,
                        file_version.file_name,
                    )

                    deleted_b2 += 1

                    print(
                        f"  ✓ Deleted B2: "
                        f"{file_version.file_name}"
                    )

                except Exception as exc:
                    failed_b2 += 1

                    print(
                        f"  ✗ Failed B2 delete: "
                        f"{file_version.file_name}"
                    )

                    print(
                        f"    Reason: {exc}"
                    )

        except Exception as exc:
            print(
                f"  ! Could not list "
                f"papers/{paper_id}: {exc}"
            )

        # -----------------------------------------------------
        # Also check the share folder
        # -----------------------------------------------------

        try:
            files = bucket.ls(
                folder_to_list=f"shares/{paper_id}",
                recursive=True,
                fetch_count=1000,
            )

            for file_version, _ in files:
                try:
                    bucket.delete_file_version(
                        file_version.id_,
                        file_version.file_name,
                    )

                    deleted_b2 += 1

                    print(
                        f"  ✓ Deleted B2: "
                        f"{file_version.file_name}"
                    )

                except Exception as exc:
                    failed_b2 += 1

                    print(
                        f"  ✗ Failed B2 delete: "
                        f"{file_version.file_name}"
                    )

                    print(
                        f"    Reason: {exc}"
                    )

        except Exception as exc:
            print(
                f"  ! Could not list "
                f"shares/{paper_id}: {exc}"
            )

    # ---------------------------------------------------------
    # 5. DELETE MONGODB SHARES
    # ---------------------------------------------------------

    print("\nDeleting MongoDB Shamir shares...")

    shares_result = shares_collection.delete_many({})

    print(
        f"  ✓ Deleted MongoDB shares: "
        f"{shares_result.deleted_count}"
    )

    # ---------------------------------------------------------
    # 6. DELETE MONGODB PAPER METADATA
    # ---------------------------------------------------------

    print("\nDeleting MongoDB paper metadata...")

    papers_result = papers_collection.delete_many({})

    print(
        f"  ✓ Deleted MongoDB papers: "
        f"{papers_result.deleted_count}"
    )

    # ---------------------------------------------------------
    # 7. SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

    print(
        f"MongoDB papers deleted : "
        f"{papers_result.deleted_count}"
    )

    print(
        f"MongoDB shares deleted : "
        f"{shares_result.deleted_count}"
    )

    print(
        f"B2 files deleted       : "
        f"{deleted_b2}"
    )

    print(
        f"B2 deletion failures   : "
        f"{failed_b2}"
    )

    print(
        "\nUsers were NOT deleted."
    )

    print(
        "Audit logs were NOT deleted."
    )

    print("\nReady for fresh testing.")


if __name__ == "__main__":
    main()