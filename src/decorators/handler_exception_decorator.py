def handle_exception(logger):

    def _handle_exception(func):
        def handle_exception_wrapper(*args):

            try:
                return func(*args)
            except Exception as e:
                logger.error(e)
                logger.error(f'Lambda function args: {args}')
                raise e

        return handle_exception_wrapper

    return _handle_exception
